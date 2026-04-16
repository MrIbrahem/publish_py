"""

"""

from dataclasses import dataclass


@dataclass
class PublicSqlSchema:
    assessments: str
    enwiki_pageviews: str
    in_process: str
    langs: str
    mdwiki_revids: str
    pages_users_to_main: str
    projects: str
    refs_counts: str
    translate_type: str
    users: str
    views_new: str
    words: str


assessments = """
CREATE TABLE
  IF NOT EXISTS assessments (
    id int unsigned NOT NULL AUTO_INCREMENT,
    title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    importance varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY title (title),
    KEY idx_assessments_title (title)
  )
"""

enwiki_pageviews = """

CREATE TABLE
  IF NOT EXISTS enwiki_pageviews (
    id int unsigned NOT NULL AUTO_INCREMENT,
    title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    en_views int DEFAULT '0',
    PRIMARY KEY (id),
    UNIQUE KEY title (title),
    KEY idx_enwiki_pageviews_title (title)
  )
"""

in_process = """

CREATE TABLE
  IF NOT EXISTS in_process (
    id int unsigned NOT NULL AUTO_INCREMENT,
    title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    lang varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
    cat varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT 'RTT',
    translate_type varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'lead',
    word int DEFAULT '0',
    add_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY title (title)
  )
"""

langs = """

CREATE TABLE
  IF NOT EXISTS langs (
    lang_id int NOT NULL AUTO_INCREMENT,
    code varchar(20) CHARACTER
    SET
      utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
      autonym varchar(70) CHARACTER
    SET
      utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
      name varchar(70) CHARACTER
    SET
      utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
      PRIMARY KEY (lang_id)
  )
"""

mdwiki_revids = """

CREATE TABLE
  IF NOT EXISTS mdwiki_revids (
    title varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    revid int NOT NULL,
    PRIMARY KEY (title)
  )
"""

pages_users_to_main = """

CREATE TABLE
  IF NOT EXISTS pages_users_to_main (
    id int unsigned NOT NULL,
    new_target varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    new_user varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    new_qid varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    KEY id (id),
    CONSTRAINT pages_users_to_main_ibfk_1 FOREIGN KEY (id) REFERENCES pages_users (id)
  )
"""

projects = """

CREATE TABLE
  IF NOT EXISTS projects (
    g_id int unsigned NOT NULL AUTO_INCREMENT,
    g_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    PRIMARY KEY (g_id),
    UNIQUE KEY g_title (g_title)
  )
"""

refs_counts = """


CREATE TABLE
  IF NOT EXISTS refs_counts (
    r_id int unsigned NOT NULL AUTO_INCREMENT,
    r_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    r_lead_refs int DEFAULT NULL,
    r_all_refs int DEFAULT NULL,
    PRIMARY KEY (r_id),
    UNIQUE KEY r_title (r_title),
    KEY idx_refs_counts_r_title (r_title)
  )
"""

translate_type = """

CREATE TABLE
  IF NOT EXISTS translate_type (
    tt_id int unsigned NOT NULL AUTO_INCREMENT,
    tt_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    tt_lead int NOT NULL DEFAULT '1',
    tt_full int NOT NULL DEFAULT '0',
    PRIMARY KEY (tt_id),
    UNIQUE KEY tt_title (tt_title),
    KEY idx_tt_title (tt_title)
  )
"""

users = """
CREATE TABLE
  IF NOT EXISTS users (
    user_id int NOT NULL AUTO_INCREMENT,
    username varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
    email varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    wiki varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
    user_group varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Uncategorized',
    reg_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
  )
"""

views_new = """

CREATE TABLE
  IF NOT EXISTS views_new (
    id int unsigned NOT NULL AUTO_INCREMENT,
    target varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    lang varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
    year int NOT NULL,
    views int DEFAULT '0',
    PRIMARY KEY (id),
    UNIQUE KEY target_lang_year (target, lang, year),
    KEY target (target)
  )
"""

words = """

CREATE TABLE
  IF NOT EXISTS words (
    w_id int unsigned NOT NULL AUTO_INCREMENT,
    w_title varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    w_lead_words int DEFAULT NULL,
    w_all_words int DEFAULT NULL,
    PRIMARY KEY (w_id),
    UNIQUE KEY w_title (w_title),
    KEY idx_words_w_title (w_title)
  )
"""

# sql_tables
sql_tables = PublicSqlSchema(
    assessments=assessments,
    enwiki_pageviews=enwiki_pageviews,
    in_process=in_process,
    langs=langs,
    mdwiki_revids=mdwiki_revids,
    pages_users_to_main=pages_users_to_main,
    projects=projects,
    refs_counts=refs_counts,
    translate_type=translate_type,
    users=users,
    views_new=views_new,
    words=words,
)
