import os
import re
from pathlib import Path


def rename_test_files_recursive(root_dir):
    root_dir = 'tests'

    # Matches files like test_v1_sqlalchemy_service.py
    file_pattern = re.compile(r'test_.*?_sqlalchemy_service\.py')

    # Matches the import line and captures the service name in Group 1
    # Note: (?:...) is a non-capturing group for the module path
    import_pattern = re.compile(
        r'from src\.sqlalchemy_app\.(?:admin|public|shared)\.services\.(.*?) import \('
    )

    if not os.path.exists(root_dir):
        print(f"Directory '{root_dir}' not found.")
        return

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if file_pattern.match(filename):
                file_path = os.path.join(dirpath, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    match = import_pattern.search(content)

                    if match:
                        service_name = match.group(1)
                        new_filename = f"test_{service_name}.py"
                        new_file_path = os.path.join(dirpath, new_filename)

                        if filename != new_filename:
                            # Check if destination already exists to prevent data loss
                            if os.path.exists(new_file_path):
                                print(f"Conflict: {new_filename} already exists in {dirpath}. Skipping.")
                            else:
                                os.rename(file_path, new_file_path)
                                print(f"Renamed: {filename} -> {new_filename}")
                        else:
                            print(f"Skipped: {filename} is already correctly named.")
                    else:
                        print(f"No matching import found in: {file_path}")

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    root_dir = Path(__file__).parent.parent / "tests/unit"
    rename_test_files_recursive(root_dir)
