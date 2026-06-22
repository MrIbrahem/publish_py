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


def delete_coordinator(coordinator_id: int) -> bool:
    return delete_record_by_pk(AdminUserRecord, coordinator_id)


def delete_qid(qid_id: int) -> bool:
    """Delete a QID record."""
    orm_obj = db.session.get(QidRecord, qid_id)
    if not orm_obj:
        raise ValueError(f"QID record with ID {qid_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(QidRecord, qid_id)
    return deleted is None


def delete_qid_other(qid_id: int) -> bool:
    """Delete a QID record."""
    orm_obj = db.session.get(QidOthersRecord, qid_id)
    if not orm_obj:
        raise ValueError(f"QID record with ID {qid_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(QidOthersRecord, qid_id)
    return deleted is None


def delete_users_no_inprocess(record_id: int) -> bool:
    """Delete a users_no_inprocess record by ID."""
    # orm_obj = db.session.query(UsersNoInprocessRecord).filter(UsersNoInprocessRecord.id == record_id).first()
    orm_obj = db.session.get(UsersNoInprocessRecord, record_id)
    if not orm_obj:
        raise ValueError(f"UsersNoInprocess record with ID {record_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(UsersNoInprocessRecord, record_id)
    return deleted is None


def delete_user(user_id: int) -> bool:
    """Delete a user record by ID."""
    orm_obj = db.session.get(UserRecord, user_id)
    if not orm_obj:
        raise ValueError(f"User record with ID {user_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(UserRecord, user_id)
    return deleted is None


def delete_full_translator(translator_id: int) -> bool:
    """Delete a full translator record by ID."""
    # orm_obj = db.session.query(FullTranslatorRecord).filter(FullTranslatorRecord.id == translator_id).first()
    orm_obj = db.session.get(FullTranslatorRecord, translator_id)
    if not orm_obj:
        raise ValueError(f"Full translator record with ID {translator_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(FullTranslatorRecord, translator_id)
    return deleted is None


def delete_report(report_id: int) -> bool:
    """Delete a report record by ID."""
    # orm_obj = db.session.query(ReportRecord).filter(ReportRecord.id == report_id).first()
    orm_obj = db.session.get(ReportRecord, report_id)
    if not orm_obj:
        raise LookupError(f"Report id {report_id} was not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(ReportRecord, report_id)
    return deleted is None


def delete_pages_users_to_main(record_id: int) -> bool:
    """Delete a pages_users_to_main record by ID."""
    orm_obj = db.session.get(PagesUsersToMainRecord, record_id)
    if not orm_obj:
        raise ValueError(f"PagesUsersToMain record with ID {record_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(PagesUsersToMainRecord, record_id)
    return deleted is None


def delete_user_page(page_id: int) -> bool:
    """Delete a page."""
    # orm_obj = db.session.query(UserPageRecord).filter(UserPageRecord.id == page_id).first()
    orm_obj = db.session.get(UserPageRecord, page_id)
    if not orm_obj:
        raise LookupError(f"Page id {page_id} was not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        logger.exception("Failed to delete user page")
        db.session.rollback()
        raise

    deleted = db.session.get(UserPageRecord, page_id)
    return deleted is None


def delete_translate_type(tt_id: int) -> bool:
    """Delete a translate_type record by ID."""
    # tt_id is the primary key for TranslateTypeRecord
    orm_obj = db.session.get(TranslateTypeRecord, tt_id)
    if not orm_obj:
        raise ValueError(f"TranslateType record with ID {tt_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(TranslateTypeRecord, tt_id)
    return deleted is None


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
    """Delete a page."""
    orm_obj = db.session.get(PageRecord, page_id)
    if not orm_obj:
        raise LookupError(f"Page id {page_id} was not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        logger.exception("Failed to delete page")
        db.session.rollback()
        raise

    deleted = db.session.get(PageRecord, page_id)
    return deleted is None


def delete_in_process(process_id: int) -> bool:
    """Delete an in_process record by ID."""
    # orm_obj = db.session.query(InProcessRecord).filter(InProcessRecord.id == process_id).first()
    orm_obj = db.session.get(InProcessRecord, process_id)
    if not orm_obj:
        raise ValueError(f"In-process record with ID {process_id} not found")

    db.session.delete(orm_obj)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    deleted = db.session.get(InProcessRecord, process_id)
    return deleted is None


def delete_project(project_id: int) -> bool:
    """Delete a project record by ID."""
    orm_obj = db.session.get(ProjectRecord, project_id)
    if not orm_obj:
        raise ValueError(f"Project record with ID {project_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(ProjectRecord, project_id)
    return deleted is None


def delete_lang(lang_id: int) -> bool:
    """Delete a language record by ID."""
    # orm_obj = db.session.query(LangRecord).filter(LangRecord.lang_id == lang_id).first()
    # lang_id is the primary key for LangRecord
    orm_obj = db.session.get(LangRecord, lang_id)
    if not orm_obj:
        raise ValueError(f"Language record with ID {lang_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(LangRecord, lang_id)
    return deleted is None


def delete_category(category_id: int) -> bool:
    """Delete a category."""
    orm_obj = db.session.get(CategoryRecord, category_id)
    if not orm_obj:
        raise ValueError(f"Category with ID {category_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(CategoryRecord, category_id)
    return deleted is None


def delete_language_setting(setting_id: int) -> bool:
    """Delete a language setting record by ID."""
    # orm_obj = db.session.query(LanguageSettingRecord).filter(LanguageSettingRecord.id == setting_id).first()
    orm_obj = db.session.get(LanguageSettingRecord, setting_id)
    if not orm_obj:
        raise ValueError(f"Language setting record with ID {setting_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(LanguageSettingRecord, setting_id)
    return deleted is None


def delete_word(word_id: int) -> bool:
    """Delete a word record by ID."""
    # orm_obj = db.session.query(WordRecord).filter(WordRecord.w_id == word_id).first()
    orm_obj = db.session.get(WordRecord, word_id)
    if not orm_obj:
        raise ValueError(f"Word record with ID {word_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(WordRecord, word_id)
    return deleted is None


def delete_views_new(view_id: int) -> bool:
    """Delete a views_new record by ID."""
    orm_obj = db.session.get(ViewsNewRecord, view_id)
    if not orm_obj:
        raise ValueError(f"ViewsNew record with ID {view_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(ViewsNewRecord, view_id)
    return deleted is None


def delete_refs_count(refs_id: int) -> bool:
    """Delete a refs_count record by ID."""
    # orm_obj = db.session.get(RefsCountRecord, refs_id)
    orm_obj = db.session.get(RefsCountRecord, refs_id)
    if not orm_obj:
        raise ValueError(f"RefsCount record with ID {refs_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(RefsCountRecord, refs_id)
    return deleted is None


def delete_mdwiki_revid(title: str) -> bool:
    """Delete an mdwiki_revid record by title."""
    orm_obj = db.session.get(MdwikiRevidRecord, title)
    if not orm_obj:
        raise ValueError(f"MDWiki revid record for '{title}' not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(MdwikiRevidRecord, title)
    return deleted is None


def delete_enwiki_pageview(pageview_id: int) -> bool:
    """Delete an enwiki pageview record by ID."""
    orm_obj = db.session.get(EnwikiPageviewRecord, pageview_id)
    if not orm_obj:
        raise ValueError(f"Enwiki pageview record with ID {pageview_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(EnwikiPageviewRecord, pageview_id)
    return deleted is None


def delete_assessment(assessment_id: int) -> bool:
    """Delete an assessment record by ID."""
    orm_obj = db.session.get(AssessmentRecord, assessment_id)
    if not orm_obj:
        raise ValueError(f"Assessment record with ID {assessment_id} not found")

    db.session.delete(orm_obj)
    db.session.commit()

    deleted = db.session.get(AssessmentRecord, assessment_id)
    return deleted is None


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
    "delete_setting",
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
