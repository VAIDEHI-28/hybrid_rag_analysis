from typing import Dict
import pandas as pd


class DataRegistry:
    """
    Central in-memory registry for all ingested Excel data.

    Structure:
    {
        "file_name.xlsx": {
            "Sheet1": pandas.DataFrame,
            "Sheet2": pandas.DataFrame,
            ...
        }
    }
    """

    def __init__(self):
        self._data: Dict[str, Dict[str, pd.DataFrame]] = {}
        self.schema: Dict[str, str] = {}  # ✅ canonical → actual column

    def register_sheet(
        self,
        file_name: str,
        sheet_name: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Register a single sheet DataFrame under a file name.
        """
        if file_name not in self._data:
            self._data[file_name] = {}

        self._data[file_name][sheet_name] = dataframe

        # 🔥 Infer schema ONCE (from first ingested sheet)
        if not self.schema:
            self.schema = self._infer_schema(dataframe)

    def _infer_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infer canonical schema from dataframe columns.
        """
        schema = {}

        for col in df.columns:
            c = col.lower()

            if "vendor" in c or "supplier" in c:
                schema["vendor"] = col
            elif "product" in c or "material" in c:
                schema["product"] = col
            elif "plant" in c:
                schema["plant"] = col
            elif "category" in c:
                schema["category"] = col
            elif "cost" in c or "spend" in c or "amount" in c:
                schema["cost"] = col
            elif "quality" in c:
                schema["quality"] = col
            elif "region" in c:
                schema["region"] = col

        return schema

    def get_sheet(self, file_name: str, sheet_name: str) -> pd.DataFrame:
        if file_name not in self._data:
            raise KeyError(f"File not found in registry: {file_name}")

        if sheet_name not in self._data[file_name]:
            raise KeyError(
                f"Sheet '{sheet_name}' not found in file '{file_name}'"
            )

        return self._data[file_name][sheet_name]

    def get_all_sheets(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        return self._data

    def list_files(self):
        return list(self._data.keys())

    def list_sheets(self, file_name: str):
        if file_name not in self._data:
            raise KeyError(f"File not found in registry: {file_name}")

        return list(self._data[file_name].keys())
