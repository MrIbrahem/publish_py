from datetime import date, timedelta
from html import escape
from urllib.parse import quote


def _fetch_yesterday_iso() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def _commas(value: int | float | str) -> str:
    """Equivalent of the `commas` Jinja filter."""
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return str(value)


class ViewsLinks:
    @staticmethod
    def build_pageviews_url(
        lang: str,
        target: str,
        pupdate: str | None = None,
        yesterday: str = "",
    ) -> str:
        """
        Constructs the target fallback URL for pageviews.wmcloud.org.
        """
        if not yesterday:
            yesterday = _fetch_yesterday_iso()

        # Format target for pageviews tool URL (replace spaces with underscores then URL-encode)
        formatted_target: str = quote(target.replace(" ", "_"))

        # Set default start date if pupdate is missing
        start_date = pupdate or "2019-01-01"

        return (
            f"https://pageviews.wmcloud.org/?project={lang}.wikipedia.org"
            f"&platform=all-access&agent=all-agents&start={start_date}"
            f"&end={yesterday}&redirects=0&pages={formatted_target}"
        )

    @staticmethod
    def build_toget_api_url(
        lang: str,
        target: str,
        pupdate: str | None = None,
    ) -> str:
        """Constructs the Wikimedia REST API URL for daily pageviews metrics."""
        # Format pupdate by removing dashes, or default to '20190101'
        start2: str = pupdate.replace("-", "") if pupdate else "20190101"

        # URL-encode target for standard API parameter
        formatted_target: str = quote(target)

        return (
            "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
            f"{lang}.wikipedia/all-access/all-agents/{formatted_target}"
            f"/daily/{start2}/2030010100"
        )

    @staticmethod
    def pageviews_link(
        views: int | float | str | None,
        lang: str,
        target: str,
        pupdate: str | None = None,
        yesterday: str = "",
    ) -> str:
        """
        Generates the main HTML link tag as a plain str.
        Attribute values and text are escaped with html.escape.
        """
        if not yesterday:
            yesterday = _fetch_yesterday_iso()

        # Generate the base Pageviews URL
        url = ViewsLinks.build_pageviews_url(lang, target, pupdate, yesterday)
        escaped_url = escape(url)

        if views:
            # Format views with commas (equivalent to views | commas)
            return f'<a href="{escaped_url}" target="_blank">{_commas(views)}</a>'

        # Generate the API URL for 'toget'
        url2 = ViewsLinks.build_toget_api_url(lang, target, pupdate)
        escaped_url2 = escape(url2)
        return f'<a target="_blank" name="toget" data-json-url="{escaped_url2}" href="{escaped_url}">?</a>'


__all__ = [
    "ViewsLinks",
]
