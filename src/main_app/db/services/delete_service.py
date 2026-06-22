""" """

from __future__ import annotations

import logging
from typing import Any, Type

from ...shared.core.extensions import db
from ..models import (
    AdminUserRecord,
    AllArticlesRecord,
    AllQidsExistRecord,
    AssessmentRecord,
    CategoryMemberRecord,
    CategoryRecord,
    EnwikiPageviewRecord,
    FullTranslatorRecord,
    InProcessRecord,
    LangRecord,
    LanguageSettingRecord,
    MdwikiRevidRecord,
    PageRecord,
    PagesUsersToMainRecord,
    ProjectRecord,
    QidOthersRecord,
    QidRecord,
    RefsCountRecord,
    ReportRecord,
    SettingRecord,
    TranslateTypeRecord,
    UserPageRecord,
    UserRecord,
    UsersNoInprocessRecord,
    UserTokenRecord,
    ViewsNewAllRecord,
    ViewsNewRecord,
    WordRecord,
)

logger = logging.getLogger(__name__)


def delete_record_by_pk(model: Type[db.Model], pk_value: Any) -> bool:  # type: ignore
    """
    Generic helper to delete a record by its primary key.
    Returns True if deleted, False otherwise.
    """
    if pk_value is None:
        return False

    try:
        # Use session.get() as it is efficient and looks up by primary key
        record = db.session.get(model, pk_value)
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting {model.__name__} with PK {pk_value}: {e}")
        db.session.rollback()
        return False


def delete_user_token(user_id: int) -> bool:
    return delete_record_by_pk(UserTokenRecord, user_id)


def delete_setting(setting_id: int) -> bool:
    return delete_record_by_pk(SettingRecord, setting_id)


def delete_setting_by_key(key: str) -> bool:
    setting = SettingRecord.query.filter_by(key=key).first()
    if setting:
        return delete_record_by_pk(SettingRecord, setting.id)
    return False


def delete_coordinator(coordinator_id: int) -> bool:
    return delete_record_by_pk(AdminUserRecord, coordinator_id)


def delete_qid(qid_id: int) -> bool:
    return delete_record_by_pk(QidRecord, qid_id)


def delete_qid_other(qid_id: int) -> bool:
    """Delete a QID record."""
    return delete_record_by_pk(QidOthersRecord, qid_id)


def delete_users_no_inprocess(record_id: int) -> bool:
    return delete_record_by_pk(UsersNoInprocessRecord, record_id)


def delete_user(user_id: int) -> bool:
    return delete_record_by_pk(UserRecord, user_id)


def delete_full_translator(translator_id: int) -> bool:
    return delete_record_by_pk(FullTranslatorRecord, translator_id)


def delete_report(report_id: int) -> bool:
    return delete_record_by_pk(ReportRecord, report_id)


def delete_pages_users_to_main(record_id: int) -> bool:
    return delete_record_by_pk(PagesUsersToMainRecord, record_id)


def delete_user_page(page_id: int) -> bool:
    return delete_record_by_pk(UserPageRecord, page_id)


def delete_translate_type(tt_id: int) -> bool:
    return delete_record_by_pk(TranslateTypeRecord, tt_id)


def delete_user_page_to_main(page_id: int) -> bool:
    """Delete the row from both ``pages_users_to_main`` and ``pages_users``.

    Returns True only when both rows are gone after the operation.
    """
    if not page_id:
        return False

    try:
        db.session.query(PagesUsersToMainRecord).filter(PagesUsersToMainRecord.id == page_id).delete(
            synchronize_session=False
        )
        db.session.query(UserPageRecord).filter(UserPageRecord.id == page_id).delete(synchronize_session=False)
        db.session.commit()
    except Exception:
        logger.exception("Failed to delete pages_users(_to_main) id=%r", page_id)
        db.session.rollback()
        return False

    in_users = db.session.get(UserPageRecord, page_id)
    in_to_main = db.session.get(PagesUsersToMainRecord, page_id)
    return in_users is None and in_to_main is None


def delete_page(page_id: int) -> bool:
    return delete_record_by_pk(PageRecord, page_id)


def delete_in_process(process_id: int) -> bool:
    return delete_record_by_pk(InProcessRecord, process_id)


def delete_project(project_id: int) -> bool:
    return delete_record_by_pk(ProjectRecord, project_id)


def delete_lang(lang_id: int) -> bool:
    return delete_record_by_pk(LangRecord, lang_id)


def delete_category(category_id: int) -> bool:
    return delete_record_by_pk(CategoryRecord, category_id)


def delete_language_setting(setting_id: int) -> bool:
    return delete_record_by_pk(LanguageSettingRecord, setting_id)


def delete_word(word_id: int) -> bool:
    return delete_record_by_pk(WordRecord, word_id)


def delete_views_new(view_id: int) -> bool:
    return delete_record_by_pk(ViewsNewRecord, view_id)


def delete_refs_count(refs_id: int) -> bool:
    return delete_record_by_pk(RefsCountRecord, refs_id)


def delete_mdwiki_revid(title: str) -> bool:
    return delete_record_by_pk(MdwikiRevidRecord, title)


def delete_enwiki_pageview(pageview_id: int) -> bool:
    return delete_record_by_pk(EnwikiPageviewRecord, pageview_id)


def delete_assessment(assessment_id: int) -> bool:
    return delete_record_by_pk(AssessmentRecord, assessment_id)


__all__ = [
    "delete_record_by_pk",
    "delete_assessment",
    "delete_category",
    "delete_coordinator",
    "delete_coordinator",
    "delete_enwiki_pageview",
    "delete_full_translator",
    "delete_in_process",
    "delete_lang",
    "delete_language_setting",
    "delete_mdwiki_revid",
    "delete_page",
    "delete_pages_users_to_main",
    "delete_project",
    "delete_qid",
    "delete_qid_other",
    "delete_record_by_pk",
    "delete_refs_count",
    "delete_report",
    "delete_setting_by_key",
    "delete_setting",
    "delete_translate_type",
    "delete_user",
    "delete_user_page",
    "delete_user_page_to_main",
    "delete_user_token",
    "delete_users_no_inprocess",
    "delete_views_new",
    "delete_word",
]
