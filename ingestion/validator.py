from pathlib import Path

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}


class ExcelValidationError(Exception):
    pass


def validate_excel_files(file_paths):
    if not file_paths:
        raise ExcelValidationError("No Excel files provided.")

    for file_path in file_paths:
        if not file_path.exists():
            raise ExcelValidationError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ExcelValidationError(
                f"Invalid file type: {file_path.name}"
            )

        if file_path.stat().st_size == 0:
            raise ExcelValidationError(
                f"Empty file detected: {file_path.name}"
            )
