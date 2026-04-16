from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SidebarItem:
    """Sidebar menu item definition."""

    id: str
    admin: int
    href: str
    title: str
    icon: str | None = None
    target: str | None = None
    disabled: bool = False


def generate_list_item(href, title, icon=None, target=None):
    """Generate HTML for a single navigation link."""
    icon_tag = f"<i class='bi {icon} me-1'></i>" if icon else ""
    target_attr = "target='_blank'" if target else ""
    link = f"""
        <a {target_attr} class='link_nav rounded' href='{href}' title='{title}'
           data-bs-toggle='tooltip' data-bs-placement='right'>
            {icon_tag}
            <span class='hide-on-collapse-inline'>{title}</span>
        </a>
    """
    return link.strip()


def create_side(active_route):
    """Generate sidebar HTML structure based on menu definitions."""
    main_menu_icons = {
        "Translations" : "bi-translate",
        "Pages" : "bi-file-text",
        "Qids" : "bi-database",
        "Users" : "bi-people",
        "Others" : "bi-three-dots",
        "Tools" : "bi-tools",
    }

    main_menu = {
        "Translations": [
            SidebarItem(
                id="last_coord",
                admin=1,
                href="last_coord",
                title="Recent",
                icon="bi-clock-history",
            )
        ],
        "Pages": [
        ],
        "Users": [
        ],
        "Others": [],
        "Tools": [],
    }

    sidebar = ["<ul class='list-unstyled'>"]

    # logger.debug(f"Generating sidebar for active_route='{active_route}'")

    for key, items in main_menu.items():
        lis = []
        group_is_active = True
        key_id = key.lower().replace(" ", "_")
        for item in items:
            if item.disabled:
                continue

            css_class = "active" if (active_route == item.href or item.href.startswith(f"{active_route}/")) else ""
            href_full = item.href if item.target else f"/admin/{item.href}"
            link = generate_list_item(href_full, item.title, item.icon, item.target)
            lis.append(f"<li id='{item.id}' class='{css_class}'>{link}</li>")

        if lis:
            show = "show" if group_is_active else ""
            expanded = "true" if group_is_active else "false"
            icon = main_menu_icons.get(key, "")
            icon_tag = f"<i class='bi {icon} me-1'></i>" if icon else ""

            group_html = f"""
                <li class="mb-1">
                    <button class="btn btn-toggle align-items-center rounded"
                            data-bs-toggle="collapse"
                            data-bs-target="#{key_id}-collapse"
                            aria-expanded="{expanded}">
                        {icon_tag}
                        <span class='hide-on-collapse-inline'>{key}</span>
                    </button>
                    <div class="collapse {show}" id="{key_id}-collapse">
                        <div class="d-none d-md-inline">
                            <!-- desktop -->
                            <ul class="btn-toggle-nav list-unstyled fw-normal pb-1 small">
                                {"".join(lis)}
                            </ul>
                        </div>
                        <div class="d-inline d-md-none">
                            <!-- mobile -->
                            <ul class="navbar-nav flex-row flex-wrap btn-toggle-nav-mobile list-unstyled fw-normal pb-1 small">
                                {"".join(lis)}
                            </ul>
                        </div>
                    </div>
                </li>
                <li class="border-top my-1"></li>
            """
            sidebar.append(group_html.strip())

    sidebar.append("</ul>")
    return "\n".join(sidebar)
