from flask import Blueprint, request, redirect, url_for, abort, Response
from typing import Dict, Any, Set

def allowed_args(args: Any, allowed_keys: Set[str]) -> Dict[str, str]:
    return {k: v for k, v in args.items() if k in allowed_keys and v != ""}

class LegacyRoutes:

    @classmethod
    def register(cls, bp: Blueprint) -> None:
        bp.add_url_rule("/leaderboard.php", view_func=cls.legacy_leaderboard, methods=["GET"])
        bp.add_url_rule("/index.php", view_func=cls.legacy_index, methods=["GET"])
        bp.add_url_rule("/missing.php", view_func=cls.legacy_missing, methods=["GET"])
        bp.add_url_rule("/sitelinks.php", view_func=cls.legacy_sitelinks, methods=["GET"])

        for path in ["/translate_med/index.php", "/translate.php", "/translate/medwiki.php", "/translate_med/medwiki.php"]:
            bp.add_url_rule(path, view_func=cls.legacy_translate, methods=["GET"])

        for path in ["/auth.php", "/auth/login.php"]:
            bp.add_url_rule(path, view_func=cls.legacy_auth, methods=["GET"])

        for path in ["/coordinator.php", "/tools.php"]:
            bp.add_url_rule(path, view_func=cls.legacy_admin, methods=["GET"])

        bp.add_url_rule("/leaderboard_js.php", view_func=cls.legacy_leaderboard_js, methods=["GET"])

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
            return redirect(url_for("leaderboard.users", username=user, **params), code=301)

        # Language Leaderboard
        if get_type == "langs" or lang:
            if not lang:
                abort(400, description="Language parameter is required for language leaderboard")
            params = allowed_args(request.args, {"year", "month", "camp"})
            return redirect(url_for("leaderboard.langs", lang_code=lang, **params), code=301)

        # Main Leaderboard
        params = allowed_args(request.args, {"year", "month", "camp", "user_group", "project"})
        return redirect(url_for("leaderboard.index", **params), code=301)

    @staticmethod
    def legacy_index() -> Response:
        params = allowed_args(request.args, {"camp", "code", "cat", "type", "filter_sparql", "exists", "doit", "nonav"})
        return redirect(url_for("td.index", **params), code=301)

    @staticmethod
    def legacy_missing() -> Response:
        params = allowed_args(request.args, {"cat", "depth", "code", "project"})
        return redirect(url_for("td.missing", **params), code=301)

    @staticmethod
    def legacy_sitelinks() -> Response:
        params = allowed_args(request.args, {"site", "title", "qid", "items_with_no_links"})
        return redirect(url_for("td.table", **params), code=301)

    @staticmethod
    def legacy_translate() -> Response:
        params = allowed_args(request.args, {"title", "code", "cat", "camp", "type", "tr_type", "word"})
        return redirect(url_for("translate_med.index", **params), code=301)

    @staticmethod
    def legacy_auth() -> Response:
        return redirect(url_for("auth.login"), code=301)

    @staticmethod
    def legacy_admin() -> Response:
        return redirect(url_for("adminpanel.index"), code=301)

    @staticmethod
    def legacy_leaderboard_js() -> Response:
        return redirect(url_for("leaderboard.index_js"), code=301)
