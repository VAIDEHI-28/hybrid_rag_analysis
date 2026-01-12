from pathlib import Path
import pandas as pd


def load_excel_file(file_path: Path) -> dict[str, pd.DataFrame]:
    """
    Load an Excel file and return all sheets as a dict.
    Key   -> sheet name
    Value -> pandas DataFrame
    """
    excel = pd.ExcelFile(file_path)
    sheets = {}

    for sheet_name in excel.sheet_names:
        df = excel.parse(sheet_name)
        sheets[sheet_name] = df

    return sheets
