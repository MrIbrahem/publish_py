import os
import re
from pathlib import Path


def rename_test_files(target_dir):

    # Regex to match the specific file naming convention
    file_pattern = re.compile(r"test_.*?_sqlalchemy_service\.py")

    # Regex to extract the service name from the import statement
    # Group 1: admin|public|shared
    # Group 2: the actual service name (e.g., category_service)
    import_pattern = re.compile(r"from src\.sqlalchemy_app\.(?:admin|public|shared)\.services\.(.*?) import \(")

    if not os.path.exists(target_dir):
        print(f"Directory '{target_dir}' not found.")
        return

    for filename in os.listdir(target_dir):
        if file_pattern.match(filename):
            file_path = os.path.join(target_dir, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                match = import_pattern.search(content)

                if match:
                    service_name = match.group(1)
                    new_filename = f"test_{service_name}.py"
                    new_file_path = os.path.join(target_dir, new_filename)

                    # Avoid overwriting if the name is already correct or exists
                    if filename != new_filename:
                        os.rename(file_path, new_file_path)
                        print(f"Renamed: {filename} -> {new_filename}")
                    else:
                        print(f"Skipped: {filename} already matches target name.")
                else:
                    print(f"No matching import found in: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    target_dir = Path(__file__).parent.parent / "tests/unit"
    rename_test_files(target_dir)
