"""Admin blueprint package."""

from flask import Blueprint, Flask

from .admin_panel import AdminPanel
from .routes import (
    AddTranslateRoutes,
    CampaignsDashboard,
    CoordinatorsRoutes,
    EmailMsgRoutes,
    FullTranslators,
    LanguageSettings,
    PagesUsersMainRoutes,
    ProjectsDashboard,
    QidsOthersRoutes,
    QidsRoutes,
    SettingsRoutes,
    StaticsRoutes,
    TranslatedRoutes,
    TranslatedUsersRoutes,
    TranslateTypeRoutes,
    UsersEmails,
    UsersNoInprocess,
)


def register_admin_blueprints(bp_admin: Blueprint) -> None:
    coordinators_bp = Blueprint("coordinators", __name__, url_prefix="/coordinators")
    coordinators_module = CoordinatorsRoutes(coordinators_bp)

    tt_bp = Blueprint("tt", __name__, url_prefix="/tt")
    tt_model = TranslateTypeRoutes(tt_bp)

    translated_bp = Blueprint("translated", __name__, url_prefix="/translated")
    translated_model = TranslatedRoutes(translated_bp)

    translated_users_bp = Blueprint("translated_users", __name__, url_prefix="/translated_users")
    translated_users_model = TranslatedUsersRoutes(translated_users_bp)

    stat_bp = Blueprint("stat", __name__, url_prefix="/stat")
    stat_model = StaticsRoutes(stat_bp)

    pages_users_to_main_bp = Blueprint("pages_users_to_main", __name__, url_prefix="/pages_users_to_main")
    pages_users_main_model = PagesUsersMainRoutes(pages_users_to_main_bp)

    bp_msg = Blueprint("email_msg", __name__, url_prefix="/email_msg")
    msg_model = EmailMsgRoutes(bp_msg)

    add_bp = Blueprint("add", __name__, url_prefix="/add")
    add_model = AddTranslateRoutes(add_bp)

    projects_module = ProjectsDashboard(Blueprint("projects", __name__, url_prefix="/projects"))

    campaigns_module = CampaignsDashboard(Blueprint("campaigns", __name__, url_prefix="/campaigns"))

    fulltranslators_module = FullTranslators(Blueprint("full_translators", __name__, url_prefix="/full_translators"))

    languagesettings_module = LanguageSettings(
        Blueprint("language_settings", __name__, url_prefix="/language_settings")
    )
    settings_module = SettingsRoutes(Blueprint("settings", __name__, url_prefix="/settings"))

    users_emails_module = UsersEmails(Blueprint("users_emails", __name__, url_prefix="/users_emails"))

    usersnoinprocess_module = UsersNoInprocess(
        Blueprint("users_no_inprocess", __name__, url_prefix="/users_no_inprocess")
    )

    qids_module = QidsRoutes(Blueprint("qids", __name__, url_prefix="/qids"))

    qids_others_module = QidsOthersRoutes(Blueprint("qids_others", __name__, url_prefix="/qids_others"))

    bp_admin.register_blueprint(coordinators_module.bp)
    bp_admin.register_blueprint(fulltranslators_module.bp)
    bp_admin.register_blueprint(usersnoinprocess_module.bp)
    bp_admin.register_blueprint(languagesettings_module.bp)
    bp_admin.register_blueprint(add_model.bp)
    bp_admin.register_blueprint(tt_model.bp)
    bp_admin.register_blueprint(translated_model.bp)
    bp_admin.register_blueprint(translated_users_model.bp)

    bp_admin.register_blueprint(msg_model.bp)
    bp_admin.register_blueprint(qids_module.bp)
    bp_admin.register_blueprint(qids_others_module.bp)
    bp_admin.register_blueprint(pages_users_main_model.bp)
    bp_admin.register_blueprint(stat_model.bp)
    bp_admin.register_blueprint(settings_module.bp)
    bp_admin.register_blueprint(projects_module.bp)
    bp_admin.register_blueprint(campaigns_module.bp)
    bp_admin.register_blueprint(users_emails_module.bp)


def register_bp_admin_blueprints(app: Flask) -> None:
    bp_admin = Blueprint("admin", __name__, url_prefix="/admin")
    admin_model = AdminPanel(bp_admin)

    register_admin_blueprints(bp_admin)

    app.register_blueprint(admin_model.bp)


__all__ = [
    "register_bp_admin_blueprints",
]
