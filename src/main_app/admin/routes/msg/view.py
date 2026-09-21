"""Admin view handlers for email message composition and dispatching."""

from __future__ import annotations

import logging

from flask import (
    Blueprint,
    render_template,
    request,
)
from flask.typing import ResponseReturnValue
from flask.views import MethodView

from ...decorators import admin_required
from .email_msg import (
    create_email_msg,
    get_current_user_email,
    get_page_data,
    get_user_email,
    make_sugustion,
    send_msg,
)

logger = logging.getLogger(__name__)


class EmailDashboardView(MethodView):
    """View to handle fetching email context and rendering the composition dashboard."""

    decorators = [admin_required]

    def get(
        self,
        last_table: str,
        id: int,
        user: str | None = None,
    ) -> str:
        """Render the email composition interface with pre-populated data."""
        # http://127.0.0.1:5000/adminpanel/email_msg?user=Mr.+Ibrahem&id=10653&last_table=pages
        logger.info("Email dashboard requested: user=%s, id=%s, last_table=%s", user, id, last_table)

        # Fetch underlying page metadata
        page_data = get_page_data(last_table, id)
        username = page_data.get("user") or user or ""

        user_email = get_user_email(str(username))
        current_user_email = get_current_user_email()

        suggestion = make_sugustion(page_data.get("lang"), page_data.get("title"))

        # Generate standard email body template
        msg = create_email_msg(page_data, suggestion)

        return render_template(
            "admins/email_msg/index.html",
            username=username,
            user_email=user_email,
            cc_me_email=current_user_email,
            html_mag=msg,
        )


class EmailSendView(MethodView):
    """View to handle sending composed email messages."""

    decorators = [admin_required]

    def post(self) -> ResponseReturnValue:
        """Process email submission form and send the email."""
        data = request.form
        msg = data.get("msg", "")
        email_to = data.get("email_to", "")
        email_from = data.get("email_from", "mdwiki.org@gmail.com")
        msg_title = data.get("msg_title", "Wiki Project Med Translation Dashboard")
        ccme = data.get("ccme", "0")
        cc_to = data.get("cc_to", "") if str(ccme) == "1" else None

        send_msg(
            msg=msg,
            email_to=email_to,
            email_from=email_from,
            msg_title=msg_title,
            cc_to=cc_to,
        )

        return render_template(
            "admins/email_msg/index.html",
            user_email=None,
            cc_me_email=None,
            msg=None,
        )


class EmailMsgView:
    """Registrar class for binding Email MethodViews to a Flask Blueprint."""

    def register(self, bp: Blueprint) -> None:
        """Register routes and endpoints on the given Blueprint with admin permissions."""
        dashboard_view = EmailDashboardView.as_view("dashboard")

        # Route bindings for the dashboard view (supporting optional 'user' parameter)
        bp.add_url_rule(
            "/dashboard/<string:last_table>/<int:id>",
            view_func=dashboard_view,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/dashboard/<string:last_table>/<int:id>/<string:user>",
            view_func=dashboard_view,
            methods=["GET"],
        )

        # Legacy endpoint alias to preserve existing url_for calls
        bp.add_url_rule(
            "/dashboard/<string:last_table>/<int:id>/<string:user>",
            endpoint="dashboard_with_user",
            view_func=dashboard_view,
            methods=["GET"],
        )

        # Route binding for sending emails
        bp.add_url_rule(
            "/send",
            view_func=EmailSendView.as_view("send"),
            methods=["POST"],
        )


__all__ = [
    "EmailDashboardView",
    "EmailSendView",
    "EmailMsgView",
]
