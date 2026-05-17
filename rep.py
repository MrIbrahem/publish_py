import os
import re

# مسارات المجلدات التي نريد فحصها
DIRS_TO_SCAN = ["src", "tests", "docs"]

# قاموس يحتوي على أنماط البحث والاستبدال
# المفتاح: نمط Regex للبحث
# القيمة: سلسلة الاستبدال (حيث $1 تشير إلى المجموعة الأولى المطابقة)
REPLACEMENTS = {
    r"services\.(assessment_service|enwiki_pageview_service|mdwiki_revid_service|refs_count_service|views_new_service|word_service)": r"services.analytics.\1",
    r"services\.(language_setting_service|setting_service)": r"services.config.\1",
    r"services\.(category_service|lang_service|project_service)": r"services.content.\1",
    r"services\.(in_process_service|page_service|translate_type_service|user_page_service)": r"services.pages.\1",
    r"services\.(pages_users_to_main_service|report_service)": r"services.reports.\1",
    r"services\.(coordinator_service|full_translator_service|user_service|user_token_service|users_no_inprocess_service)": r"services.users.\1",
    r"services\.(allqid_service|qid_service)": r"services.wikidata.\1",
}


def process_file(filepath):
    """دالة لقراءة الملف، تطبيق الاستبدالات، وحفظه إذا تم التعديل"""
    try:
        # استخدام ترميز utf-8 لتجنب مشاكل اللغة العربية إن وجدت
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        for pattern, replacement in REPLACEMENTS.items():
            # إضافة (?<![.\w]) قبل النمط و (?!\w) بعده
            # لضمان أننا نطابق الكلمة كاملة ولا نكسر مسارات أخرى موجودة بالفعل
            # مثال: لا نستبدل services.analytics.assessment_service إلى services.analytics.analytics.assessment_service
            full_pattern = r"\b" + pattern + r"\b"

            # تطبيق الاستبدال
            content = re.sub(full_pattern, replacement, content)

        # إذا حدث أي تغيير في المحتوى، نحفظ الملف
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

    return False


def main():
    modified_files_count = 0

    for directory in DIRS_TO_SCAN:
        if not os.path.exists(directory):
            print(f"Directory '{directory}' does not exist. Skipping...")
            continue

        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".py") or filename.endswith(".md"):
                    filepath = os.path.join(root, filename)
                    if process_file(filepath):
                        print(f"Updated: {filepath}")
                        modified_files_count += 1

    print(f"\nDone! Modified {modified_files_count} files.")


if __name__ == "__main__":
    main()
