from ingestion.registry import DataRegistry
from ingestion.loader import load_excel_file
from ingestion.validator import validate_excel_files
from schema.schema_service import SchemaService
from pathlib import Path


def run_schema_test():
    registry = DataRegistry()

    upload_dir = Path("data/uploads")
    excel_files = list(upload_dir.glob("*.xlsx"))

    validate_excel_files(excel_files)

    for file_path in excel_files:
        sheets = load_excel_file(file_path)
        for sheet_name, df in sheets.items():
            registry.register_sheet(
                file_name=file_path.name,
                sheet_name=sheet_name,
                dataframe=df
            )

    schema_service = SchemaService(registry)
    schema = schema_service.infer_and_store_schema()

    print("\nInferred Schema Mapping:")
    for canonical, column in schema.items():
        print(f"  {canonical}  ->  {column}")


if __name__ == "__main__":
    run_schema_test()
