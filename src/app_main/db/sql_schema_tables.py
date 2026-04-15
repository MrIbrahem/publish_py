""" """

from dataclasses import dataclass


@dataclass
class TablesCreatesSql:
    categories: str
    pages: str
    pages_users: str
    publish_reports: str
    qids: str
    user_tokens: str


categories = """
CREATE TABLE IF NOT EXISTS categories (
    id int unsigned NOT NULL AUTO_INCREMENT,
    category varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    category2 varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    display varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    campaign varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    depth int DEFAULT NULL,
    def int NOT NULL DEFAULT '0',
    PRIMARY KEY (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
"""

pages = """
CREATE TABLE IF NOT EXISTS pages (
    id int unsigned NOT NULL AUTO_INCREMENT,
    title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    word int DEFAULT NULL,
    translate_type varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    cat varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    lang varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    user varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    target varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    date date DEFAULT NULL,
    pupdate varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted int DEFAULT '0',
    mdwiki_revid int DEFAULT NULL,
    PRIMARY KEY (id),
    KEY idx_title (title),
    KEY target (target)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
"""

pages_users = """
CREATE TABLE IF NOT EXISTS pages_users (
    id int unsigned NOT NULL AUTO_INCREMENT,
    title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    word int DEFAULT NULL,
    translate_type varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    cat varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    lang varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    user varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    target varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    date date DEFAULT NULL,
    pupdate varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted int DEFAULT '0',
    mdwiki_revid int DEFAULT NULL,
    PRIMARY KEY (id),
    KEY idx_title (title),
    KEY target (target)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
"""

publish_reports = """
CREATE TABLE IF NOT EXISTS publish_reports (
    id int NOT NULL AUTO_INCREMENT,
    date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    lang varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    sourcetitle varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    result varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    data longtext CHARACTER
    SET
        utf8mb4 COLLATE utf8mb4_bin NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT publish_reports_chk_1 CHECK (json_valid (data))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
"""

qids = """
CREATE TABLE IF NOT EXISTS qids (
    id int unsigned NOT NULL AUTO_INCREMENT,
    title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    qid varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
    add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY title (title),
    KEY qid (qid)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
"""

user_tokens = """
CREATE TABLE IF NOT EXISTS user_tokens (
    user_id int NOT NULL,
    username varchar(255) NOT NULL,
    access_token varbinary(1024) NOT NULL,
    access_secret varbinary(1024) NOT NULL,
    created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_used_at datetime DEFAULT NULL,
    rotated_at datetime DEFAULT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_user_tokens_username (username)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
"""

# sql_tables
sql_tables = TablesCreatesSql(
    categories=categories,
    pages=pages,
    pages_users=pages_users,
    publish_reports=publish_reports,
    qids=qids,
    user_tokens=user_tokens,
)
