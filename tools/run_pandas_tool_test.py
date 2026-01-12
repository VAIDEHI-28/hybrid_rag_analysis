from pathlib import Path
from ingestion.loader import load_excel_file
from ingestion.validator import validate_excel_files
from ingestion.registry import DataRegistry
from schema.schema_service import SchemaService
from tools.pandas_tool import PandasAnalyticsTool


def run_pandas_tool_test():
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

    # Get first dataframe
    data = registry.get_all_sheets()
    file = next(iter(data))
    sheet = next(iter(data[file]))
    df = data[file][sheet]

    tool = PandasAnalyticsTool(df, schema)

    print("\nTotal Cost:")
    print(tool.aggregate(metric="cost", operation="sum"))

    print("\nCost by Vendor:")
    print(tool.aggregate(metric="cost", operation="sum", group_by="vendor"))

    print("\nTop Vendor by Cost:")
    print(tool.top_k(metric="cost", by="vendor", k=1))

    print("\nTop Category by Cost:")
    print(tool.top_k(metric="cost", by="category", k=1))


if __name__ == "__main__":
    run_pandas_tool_test()
