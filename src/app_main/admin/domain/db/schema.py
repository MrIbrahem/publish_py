"""
CREATE TABLE
  IF NOT EXISTS coordinator (
    id int unsigned NOT NULL AUTO_INCREMENT,
    user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    active int NOT NULL DEFAULT '1',
    PRIMARY KEY (id),
    UNIQUE KEY user (user)
  )
CREATE TABLE
  IF NOT EXISTS full_translators (
    id int unsigned NOT NULL AUTO_INCREMENT,
    user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    active int NOT NULL DEFAULT '1',
    PRIMARY KEY (id),
    UNIQUE KEY user (user)
  )
CREATE TABLE
  IF NOT EXISTS language_settings (
    id int NOT NULL AUTO_INCREMENT,
    lang_code varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    move_dots tinyint DEFAULT '0',
    expend tinyint DEFAULT '0',
    add_en_lang tinyint DEFAULT '0',
    add_en_lng tinyint DEFAULT '0',
    PRIMARY KEY (id),
    UNIQUE KEY lang_code (lang_code)
  )
CREATE TABLE
  IF NOT EXISTS settings (
    id int NOT NULL AUTO_INCREMENT,
    title varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
    displayed varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
    Type varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'check',
    value int NOT NULL DEFAULT '0',
    ignored int NOT NULL DEFAULT '0',
    PRIMARY KEY (id),
    UNIQUE KEY title (title),
    KEY idx_title (title)
  )
CREATE TABLE
  IF NOT EXISTS users_no_inprocess (
    id int unsigned NOT NULL AUTO_INCREMENT,
    user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    active int NOT NULL DEFAULT '1',
    PRIMARY KEY (id),
    UNIQUE KEY user (user)
  )
"""

from dataclasses import dataclass


@dataclass
class TablesCreatesSql:
    coordinator: str
    full_translators: str
    language_settings: str
    settings: str
    users_no_inprocess: str


# sql_tables
sql_tables = TablesCreatesSql(
    coordinator=coordinator,
    full_translators=full_translators,
    language_settings=language_settings,
    settings=settings,
    users_no_inprocess=users_no_inprocess,
)
