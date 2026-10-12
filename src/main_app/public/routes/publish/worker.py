"""
Post/Publish endpoint worker for Content Translation.

Structure:
    RequestValidator  : filters + validates the incoming request (marshmallow)
    ErrorFileResolver : decides which "to_do" file a result belongs to
    ReportRecorder    : writes the to_do file + inserts the report row
    WikidataLinker    : links the new page to Wikidata (with fallback user)
    PublishWorker     : one instance per request, runs the whole workflow

The only public entry point is `handle_form`.
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Response, jsonify
from marshmallow import ValidationError

from ....database.models import LanguageSettingRecord
from ....database.services import (
    LanguageSettingService,
    MdwikiRevidService,
    UserTokenService,
    WordService,
)
from ....services.clients import MediaWikiApiClient
from ....services.schemas import PublishRequestSchema
from ....services.utils.helpers import do_changes_to_text_with_settings
from ....services.utils.helpers.format import Formatter
from .error_resolver import ErrorFileResolver
from .report_recorder import ReportRecorder
from .to_db import add_to_db_tab
from .wikidata_linker import WikidataLinker

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Request validation
# --------------------------------------------------------------------------- #
class RequestValidator:
    """Filters request data and validates it with the marshmallow schema."""

    @staticmethod
    def filter_request_data(request_data: dict[str, Any]) -> dict[str, Any]:
        raw = {k: v for k, v in request_data.items() if v != "" and str(v).lower() != "all"}

        # translate_type can be "all" - only include if present in request
        translate_type = request_data.get("translate_type", "")
        if translate_type:
            raw["translate_type"] = translate_type
        return raw

    @staticmethod
    def _error_response(info: Any) -> Response:
        response = jsonify({"error": {"code": "validation_error", "info": info}})
        response.status_code = 400
        return response

    def validate(
        self,
        request_data: dict[str, Any],
    ) -> tuple[dict[str, Any] | None, Response | None]:
        """Validate the request.

        Returns:
            (validated_dict, None) on success, (None, error_response) on failure.
        """
        raw = self.filter_request_data(request_data)

        try:
            validated_data = PublishRequestSchema().load(raw, unknown="exclude")
        except ValidationError as err:
            return None, self._error_response(err.messages)

        if validated_data is None:
            return None, self._error_response("")

        validated_dict = {k: v for k, v in validated_data.items() if v is not None}  # type: ignore

        return validated_dict, None


# --------------------------------------------------------------------------- #
# Main worker
# --------------------------------------------------------------------------- #
class PublishWorker:
    """Handles one publish request end-to-end (one instance per request)."""

    def __init__(
        self,
        request_data: dict[str, Any],
        *,
        validator: RequestValidator | None = None,
        token_service: UserTokenService | None = None,
        recorder: ReportRecorder | None = None,
        wikidata_linker: WikidataLinker | None = None,
    ) -> None:
        self.request_data = request_data
        self.token_service = token_service or UserTokenService()
        self.recorder = recorder or ReportRecorder()

        self.validator = validator or RequestValidator()
        self.wikidata_linker = wikidata_linker or WikidataLinker(self.recorder, self.token_service)

        # Per-request state (filled while running)
        self.text: str = ""
        self.tab: dict[str, Any] = {}
        self.access_key: str = ""
        self.access_secret: str = ""

    # ------------------------------------------------------------------ #
    # Entry point
    # ------------------------------------------------------------------ #
    def run(self) -> Response:
        validated_dict, error_response = self.validator.validate(self.request_data)

        if error_response is not None:
            return error_response

        if validated_dict is None:
            return self.validator._error_response("")

        self.text = validated_dict.get("text", "")

        # Build operation metadata
        self.tab = self._build_tab(validated_dict)

        # Get access credentials
        user_token = self.token_service.get_user_token_by_username(self.tab["user"])

        if user_token is None:
            response = jsonify(self._handle_no_access())
            response.status_code = 403
            return response

        # Get credentials
        self.access_key, self.access_secret = user_token.decrypted()

        # Add captcha parameters if present
        self._add_captcha_params(validated_dict)

        return jsonify(self.process())

    # ------------------------------------------------------------------ #
    # Request preparation
    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_tab(validated_dict: dict[str, Any]) -> dict[str, Any]:
        """Build operation metadata from the validated request."""
        return {
            "title": Formatter.format_title(validated_dict.get("title", "")),
            "summary": "",
            "lang": validated_dict.get("target", ""),
            "user": Formatter.format_user(validated_dict.get("user", "")),
            "campaign": validated_dict.get("campaign", ""),
            "result": "",
            "edit": {},
            "sourcetitle": validated_dict.get("sourcetitle", ""),
            "request_revid": validated_dict.get("revid", "") or validated_dict.get("revision", ""),
            "translate_type": validated_dict.get("translate_type", "lead"),
            "words": 0,
        }

    def _add_captcha_params(self, validated_dict: dict[str, Any]) -> None:
        if validated_dict.get("wpCaptchaId") and validated_dict.get("wpCaptchaWord"):
            self.tab["wp_captcha_params"] = {
                "wpCaptchaId": validated_dict["wpCaptchaId"],
                "wpCaptchaWord": validated_dict["wpCaptchaWord"],
            }

    # ------------------------------------------------------------------ #
    # Workflow steps
    # ------------------------------------------------------------------ #
    def _resolve_revision_info(self) -> None:
        """Fill `words` and `revid` in tab (mirrors PHP $tab['words'])."""
        self.tab["words"] = self._get_word_count(self.tab["sourcetitle"])

        # Get revision ID
        mdwiki_revid = self._get_revid(self.tab["sourcetitle"])

        if not mdwiki_revid:
            self.tab["empty revid"] = "Can not get revid"
            mdwiki_revid = self.tab.get("request_revid", "")

        self.tab["revid"] = mdwiki_revid

    def _fix_text(self) -> None:
        """Apply text changes (fix references etc.) according to language settings."""
        language_setting = self._load_language_settings(self.tab["lang"])

        newtext = do_changes_to_text_with_settings(
            text=self.text,
            title=self.tab["title"],
            lang=self.tab["lang"],
            source_title=self.tab["sourcetitle"],
            mdwiki_revid=self.tab["revid"],
            move_dots=bool(language_setting.move_dots),
            expend_infobox=bool(language_setting.expend),
            add_en_lang=bool(language_setting.add_en_lang),
            # add_category=add_category,
        )

        if newtext:
            self.tab["fix_refs"] = "yes" if newtext != self.text else "no"
            self.text = newtext

    def _build_api_params(self) -> dict[str, Any]:
        hashtag = Formatter.determine_hashtag(self.tab["title"], self.tab["user"])
        self.tab["summary"] = Formatter.make_summary(
            self.tab["revid"],
            self.tab["sourcetitle"],
            self.tab["lang"],
            hashtag,
        )

        # Prepare API parameters
        api_params = {
            "action": "edit",
            "title": self.tab["title"],
            "summary": self.tab["summary"],
            "text": self.text,
            "format": "json",
        }

        # Add captcha parameters if present
        if self.tab.get("wp_captcha_params"):
            api_params.update(self.tab["wp_captcha_params"])

        return api_params

    def _after_success(self, editit: dict[str, Any]) -> None:
        """Link to Wikidata and save to the database after a successful edit."""
        link_to_wd = self.wikidata_linker.link(
            self.tab["sourcetitle"],
            self.tab["lang"],
            self.tab["user"],
            self.tab["title"],
            self.access_key,
            self.access_secret,
        )

        sql_result = add_to_db_tab(
            link_to_wd,
            self.tab,
        )

        editit["LinkToWikidata"] = link_to_wd
        editit["sql_result"] = sql_result

    def _record(self, to_do_file: str) -> None:
        self.recorder.record(
            self.tab,
            to_do_file,
            title=self.tab["title"],
            user=self.tab["user"],
            lang=self.tab["lang"],
            sourcetitle=self.tab["sourcetitle"],
        )

    def process(self) -> dict[str, Any]:
        """Run the edit workflow and return the edit result."""
        self._resolve_revision_info()
        self._fix_text()
        api_params = self._build_api_params()

        # Perform the edit
        editit = MediaWikiApiClient.publish_do_edit(
            api_params,
            self.tab["lang"],
            self.access_key,
            self.access_secret,
        )

        success = editit.get("edit", {}).get("result", "")
        self.tab["result"] = success

        if success == "Success":
            self._after_success(editit)

        self.tab["result_to_cx"] = editit

        to_do_file = ErrorFileResolver.for_edit(editit)
        self._record(to_do_file)

        return editit

    def _handle_no_access(self) -> dict[str, Any]:
        """Handle the case when the user has no access credentials."""
        user = self.tab["user"]
        error = {"code": "noaccess", "info": "noaccess"}
        editit = {
            "error": error,
            "edit": {"error": error, "username": user},
            "username": user,
        }
        self.tab["result_to_cx"] = editit
        self._record("noaccess")

        return editit

    # ------------------------------------------------------------------ #
    # Data lookups
    # ------------------------------------------------------------------ #
    @staticmethod
    def _get_word_count(title: str) -> int:
        """Get word count for an article title (0 if not found).

        Mirrors PHP: `$word = $Words_table[$title] ?? 0;`
        """
        lead_words, _ = WordService().get_word_counts_for_title(title)
        return lead_words or 0

    @staticmethod
    def _load_language_settings(lang: str) -> LanguageSettingRecord:
        """Load language settings for the given language."""
        service = LanguageSettingService()
        return service.get_language_setting_by_code(lang) or LanguageSettingRecord()

    @staticmethod
    def _get_revid(sourcetitle: str) -> str | int:
        # title is the primary_key for MdwikiRevidRecord
        record = MdwikiRevidService().get_mdwiki_revid_by_title(sourcetitle)
        if record:
            return record.revid
        return ""


# --------------------------------------------------------------------------- #
# Public API (the only function used from outside)
# --------------------------------------------------------------------------- #
def handle_form(request_data: dict[str, Any]) -> Response:
    return PublishWorker(request_data).run()


__all__ = [
    "handle_form",
]
