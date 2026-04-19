""" """

from dataclasses import dataclass


@dataclass
class TablesCreatesSql:
    coordinators: str
    full_translators: str
    language_settings: str
    settings: str
    users_no_inprocess: str


coordinators = """

CREATE TABLE IF NOT EXISTS coordinators (
    id int unsigned NOT NULL AUTO_INCREMENT,
    username varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    is_active int NOT NULL DEFAULT '1',
    PRIMARY KEY (id),
    UNIQUE KEY username (username)
  )
"""

full_translators = """

CREATE TABLE IF NOT EXISTS full_translators (
    id int unsigned NOT NULL AUTO_INCREMENT,
    user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    active int NOT NULL DEFAULT '1',
    PRIMARY KEY (id),
    UNIQUE KEY user (user)
  )
"""

language_settings = """
CREATE TABLE IF NOT EXISTS language_settings (
    id int NOT NULL AUTO_INCREMENT,
    lang_code varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    move_dots tinyint DEFAULT '0',
    expend tinyint DEFAULT '0',
    add_en_lang tinyint DEFAULT '0',
    PRIMARY KEY (id),
    UNIQUE KEY lang_code (lang_code)
  )
"""

# Type -> form_type
settings = """
    CREATE TABLE IF NOT EXISTS settings (
        `id` INT NOT NULL AUTO_INCREMENT,
        `key` VARCHAR(190) NOT NULL,
        `title` VARCHAR(500) NOT NULL,
        `value` text DEFAULT NULL,
        `value_type` enum ('boolean', 'string', 'integer', 'json') NOT NULL DEFAULT 'boolean',
        PRIMARY KEY (`id`),
        UNIQUE KEY unique_key (`key`)
    )
"""

users_no_inprocess = """

CREATE TABLE IF NOT EXISTS users_no_inprocess (
    id int unsigned NOT NULL AUTO_INCREMENT,
    user varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
    active int NOT NULL DEFAULT '1',
    PRIMARY KEY (id),
    UNIQUE KEY user (user)
  )

"""

admin_sql_tables = TablesCreatesSql(
    coordinators=coordinators,
    full_translators=full_translators,
    language_settings=language_settings,
    settings=settings,
    users_no_inprocess=users_no_inprocess,
)
