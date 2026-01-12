from pathlib import Path
from ingestion.validator import validate_excel_files
from ingestion.loader import load_excel_file
from ingestion.registry import DataRegistry


def run_ingestion():
    upload_dir = Path("data/uploads")
    excel_files = list(upload_dir.glob("*.xlsx"))

    print(f"Found {len(excel_files)} Excel file(s).")
    validate_excel_files(excel_files)

    registry = DataRegistry()

    for file_path in excel_files:
        print(f"\nLoading file: {file_path.name}")
        sheets = load_excel_file(file_path)

        for sheet_name, df in sheets.items():
            registry.register_sheet(
                file_name=file_path.name,
                sheet_name=sheet_name,
                dataframe=df
            )
            print(
                f"  Sheet: {sheet_name} | "
                f"Rows: {df.shape[0]} | "
                f"Columns: {list(df.columns)}"
            )

    print("\nIngestion completed successfully.")
    print(f"Total sheets registered: {len(registry.get_all_sheets())}")


if __name__ == "__main__":
    run_ingestion()
