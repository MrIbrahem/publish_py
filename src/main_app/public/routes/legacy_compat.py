from typing import Any

from flask import Blueprint, abort, redirect, request, url_for
from werkzeug.wrappers.response import Response


def allowed_args(args: Any, allowed_keys: set[str]) -> dict[str, str]:
    return {k: v for k, v in args.items() if k in allowed_keys and v != ""}


def map_query_types(params: dict[str, str]) -> dict[str, str]:
    if params.get("type") in ["all", "lead"]:
        params["tr_type"] = params["type"]
        params.pop("type", None)
    return params


class LegacyRoutes:

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        bp.add_url_rule("/Translation_Dashboard/leaderboard.php", view_func=cls.legacy_leaderboard, methods=["GET"])
        bp.add_url_rule("/Translation_Dashboard/index.php", view_func=cls.legacy_index, methods=["GET"])

        for path in [
            "/Translation_Dashboard/translate_med/index.php",
            "/Translation_Dashboard/translate_med/medwiki.php",
            "/Translation_Dashboard/translate/medwiki.php",
            "/Translation_Dashboard/translate.php",
        ]:
            bp.add_url_rule(path, view_func=cls.legacy_translate, methods=["GET"])

    @staticmethod
    def legacy_leaderboard() -> Response:
        get_type = request.args.get("get", "").strip().lower()
        user = request.args.get("user", "").strip()
        lang = (request.args.get("langcode") or request.args.get("lang") or "").strip()

        # User Leaderboard
        if get_type == "users" or user:
            if not user:
                abort(400, description="User parameter is required for user leaderboard")
            params = allowed_args(request.args, {"year", "month", "camp", "langcode", "lang"})
            url = url_for("leaderboard.users", username=user, **params)  # pyright: ignore[reportArgumentType]
            return redirect(url, code=301)

        # Language Leaderboard
        if get_type == "langs" or lang:
            if not lang:
                abort(400, description="Language parameter is required for language leaderboard")
            params = allowed_args(request.args, {"year", "month", "camp"})
            url = url_for("leaderboard.langs", lang_code=lang, **params)  # pyright: ignore[reportArgumentType]
            return redirect(url, code=301)

        # Main Leaderboard
        params = allowed_args(request.args, {"year", "month", "camp", "user_group", "project"})
        url = url_for("leaderboard.index", **params)  # pyright: ignore[reportArgumentType]
        return redirect(url, code=301)

    @staticmethod
    def legacy_index() -> Response:
        # ?camp=Main&code=ady&tr_type=lead&doit=Do+it
        """Handle legacy index route and redirect to the new target destination index.

        Parses allowed query parameters from the incoming request and performs a
        params = allowed_args(request.args, {"camp", "code", "cat", "type", "tr_type", "doit"})
        return redirect(url_for("td.index", **params), code=301)
        301 Permanent Redirect to the 'td.index' endpoint with the filtered parameters.

        Returns:
            Response: A redirect response object with HTTP status code 301.
        """
        # ?camp=Main&code=ady&tr_type=lead&doit=Do+it
        params = allowed_args(request.args, {"camp", "code", "cat", "type", "tr_type", "doit"})
        params = map_query_types(params)

        doit = request.args.get("doit", "").strip()
        if doit:
            url = url_for("td.table", **params)  # pyright: ignore[reportArgumentType]
            return redirect(url, code=301)

        url = url_for("td.index", **params)  # pyright: ignore[reportArgumentType]
        return redirect(url, code=301)

    @staticmethod
    def legacy_translate() -> Response:
        params = allowed_args(request.args, {"title", "langcode", "code", "cat", "camp", "type", "tr_type", "word"})

        params = map_query_types(params)

        if params.get("code"):
            params["langcode"] = params["code"]
            params.pop("code", None)

        url = url_for("translate_med.index", **params)  # pyright: ignore[reportArgumentType]
        return redirect(url, code=301)
