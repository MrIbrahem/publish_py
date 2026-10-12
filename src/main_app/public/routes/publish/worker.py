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

import json
import logging
from typing import Any

from flask import Response, jsonify
from marshmallow import ValidationError

from ....config import app_settings
from ....database.models import LanguageSettingRecord
from ....database.services import (
    LanguageSettingService,
    MdwikiRevidService,
    ReportService,
    UserTokenService,
    WordService,
)
from ....services.clients import (
    get_title_info,
    link_to_wikidata,
    publish_do_edit,
)
from ....services.schemas import PublishRequestSchema
from ....services.utils.helpers import (
    determine_hashtag,
    do_changes_to_text_with_settings,
    make_summary,
    to_do,
)
from ....services.utils.helpers.format import format_title, format_user
from .to_db import add_to_db_tab

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
# Error file resolution
# --------------------------------------------------------------------------- #
class ErrorFileResolver:
    """Maps edit / Wikidata results to the name of the to_do file."""

    MAIN_ERRORS: tuple[str, ...] = (
        "protectedpage",
        "titleblacklist",
        "ratelimited",
        "editconflict",
        "spam filter",
        "abusefilter",
        "mwoauth-invalid-authorization",
    )
    WIKIDATA_ERRORS: dict[str, str] = {
        "Links to user pages": "wd_user_pages",
        "get_csrftoken": "wd_csrftoken",
        "protectedpage": "wd_protectedpage",
    }

    @classmethod
    def resolve(cls, editit: Any, placeholder: str) -> str:
        """Determine the appropriate error file based on error content.

        Args:
            editit: Edit (or link) result
            placeholder: Default file name ("errors" for edits, else Wikidata)
        """
        c_text = json.dumps(editit)

        if placeholder == "errors":
            for err in cls.MAIN_ERRORS:
                if err in c_text:
                    return err
        else:
            for err, file_name in cls.WIKIDATA_ERRORS.items():
                if err in c_text:
                    return file_name

        return placeholder

    @classmethod
    def for_edit(cls, editit: dict[str, Any]) -> str:
        """Pick the to_do file for the result of the edit request."""
        edit = editit.get("edit", {})
        if edit.get("result", "") == "Success":
            return "success"
        if edit.get("captcha"):
            return "captcha"
        return cls.resolve(editit, "errors")


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
class ReportRecorder:
    """Saves an operation to the to_do file and to the reports table."""

    def __init__(self, report_service: ReportService | None = None) -> None:
        self.report_service = report_service or ReportService()

    def record(
        self,
        data: dict[str, Any],
        file_name: str,
        *,
        title: str,
        user: str,
        lang: str,
        sourcetitle: str,
    ) -> None:
        to_do(data, file_name)

        self.report_service.add_report(
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
            result=file_name,
            data=json.dumps(data),
        )


# --------------------------------------------------------------------------- #
# Wikidata
# --------------------------------------------------------------------------- #
class WikidataLinker:
    """Links a published page to Wikidata, retrying with a fallback user."""

    def __init__(
        self,
        recorder: ReportRecorder,
        token_service: UserTokenService | None = None,
    ) -> None:
        self.recorder = recorder
        self.token_service = token_service or UserTokenService()

    @staticmethod
    def _should_link(lang: str, title: str) -> bool:
        """Return False if the page is missing or is a user page (ns 2)."""
        page_information = get_title_info(title, lang)
        if not page_information:
            return False

        # skip link to wd for user pages
        return page_information.get("ns", None) != 2

    def _retry_with_fallback_user(
        self,
        sourcetitle: str,
        lang: str,
        title: str,
        user: str,
    ) -> dict[str, Any]:
        """Retry Wikidata linking with fallback user credentials."""
        fallback_user = app_settings.users.fallback_user
        logger.debug(f"get_csrftoken failed for user: {user}, retrying with {fallback_user}")

        # Retry with fallback user credentials
        fallback_token = self.token_service.get_user_token_by_username(fallback_user)

        if fallback_token is None:
            return {}

        fallback_access_key, fallback_access_secret = fallback_token.decrypted()
        link_result = link_to_wikidata(
            sourcetitle,
            lang,
            fallback_user,
            title,
            fallback_access_key,
            fallback_access_secret,
        )

        if "error" not in link_result:
            link_result["fallback_user"] = fallback_user
            link_result["original_user"] = user
            logger.debug(f"Successfully linked using {fallback_user} fallback credentials")
        return link_result

    def _record_error(
        self,
        link_result: dict[str, Any],
        sourcetitle: str,
        lang: str,
        user: str,
        title: str,
    ) -> None:
        tab3 = {
            "error": link_result["error"],
            "qid": link_result.get("qid", ""),
            "title": title,
            "sourcetitle": sourcetitle,
            "fallback": link_result.get("fallback", ""),
            "lang": lang,
            "username": user,
        }
        file_name = ErrorFileResolver.resolve(link_result.get("error", {}), "wd_errors")

        # Insert to reports
        self.recorder.record(
            tab3,
            file_name,
            title=title,
            user=user,
            lang=lang,
            sourcetitle=sourcetitle,
        )

    def link(
        self,
        sourcetitle: str,
        lang: str,
        user: str,
        title: str,
        access_key: str,
        access_secret: str,
    ) -> dict[str, Any]:
        """
        Run the post-edit Wikidata linking and record any error.

        Args:
            sourcetitle: Source page title
            lang: Target language code
            user: Username
            title: Target page title
            access_key: OAuth access key
            access_secret: OAuth access secret

        Returns:
            Wikidata link result
        """
        if not self._should_link(lang, title):
            # skip link to wd for user pages
            return {"error": "skip link to wd for user pages"}

        link_result = link_to_wikidata(sourcetitle, lang, user, title, access_key, access_secret)

        # Check if the error is get_csrftoken failure and user is not already the fallback user
        fallback_user = app_settings.users.fallback_user
        if link_result.get("error") == "get_csrftoken failed" and user != fallback_user:
            link_result["fallback"] = self._retry_with_fallback_user(sourcetitle, lang, title, user)

        if "error" in link_result:
            self._record_error(link_result, sourcetitle, lang, user, title)

        return link_result


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
            "title": format_title(validated_dict.get("title", "")),
            "summary": "",
            "lang": validated_dict.get("target", ""),
            "user": format_user(validated_dict.get("user", "")),
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
        hashtag = determine_hashtag(self.tab["title"], self.tab["user"])
        self.tab["summary"] = make_summary(
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
        editit = publish_do_edit(
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
