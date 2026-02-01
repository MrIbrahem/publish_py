"""Title and user formatting utilities.

Mirrors: php_src/endpoints/post.php (formatTitle, formatUser, determineHashtag, make_summary)
"""

from ..config import settings


def format_title(title: str) -> str:
    """Format page title.

    Args:
        title: Raw page title

    Returns:
        Formatted title with underscores replaced and special user paths normalized
    """
    title = title.replace("_", " ")
    # Normalize special user paths based on config
    for alt_user, canonical_user in settings.users.special_users.items():
        title = title.replace(f"{alt_user}/", f"{canonical_user}/")
    return title


def format_user(user: str) -> str:
    """Format username, applying special user mappings.

    Args:
        user: Raw username

    Returns:
        Formatted username with underscores replaced and special users mapped
    """
    user = settings.users.special_users.get(user, user)
    return user.replace("_", " ")


def determine_hashtag(title: str, user: str) -> str:
    """Determine appropriate hashtag based on title and user.

    Args:
        title: Page title
        user: Username

    Returns:
        Hashtag string (empty for user's own pages)
    """
    hashtag = "#mdwikicx"
    # Users without hashtag on their own pages (check for user path pattern)
    for exempt_user in settings.users.users_without_hashtag:
        # Match user pages like "Username/..." or exact username match in title
        if (f"{exempt_user}/" in title or title == exempt_user) and user == exempt_user:
            hashtag = ""
            break
    return hashtag


def make_summary(revid: str, sourcetitle: str, target_lang: str, hashtag: str = "#mdwikicx") -> str:
    """Generate edit summary for translation.

    Args:
        revid: Source revision ID
        sourcetitle: Source page title
        target_lang: Target language code
        hashtag: Campaign hashtag

    Returns:
        Edit summary string
    """
    return f"Created by translating the page [[:mdwiki:Special:Redirect/revision/{revid}|{sourcetitle}]] to:{target_lang} {hashtag}"
