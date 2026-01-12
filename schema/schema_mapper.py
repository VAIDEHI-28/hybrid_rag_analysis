from typing import Dict, List
import pandas as pd


class SchemaMapper:
    """
    Infers semantic meaning of columns in a dataframe.
    Maps raw column names to canonical business concepts.
    """

    CANONICAL_SCHEMA = {
        "vendor": ["vendor", "supplier", "partner"],
        "plant": ["plant", "location", "factory", "site"],
        "cost": ["cost", "spend", "amount", "expense", "price"],
        "product": ["product", "item", "material", "sku"],
        "category": ["category", "segment", "type"],
        "region": ["region", "zone", "area"],
        "lead_time": ["lead", "delivery", "days", "time"],
        "quality": ["quality", "rating", "score"],
    }

    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
        self.mapping: Dict[str, str] = {}

    def infer(self) -> Dict[str, str]:
        """
        Infer schema by matching column names to canonical meanings.
        """
        for column in self.dataframe.columns:
            normalized = column.lower()

            for canonical, keywords in self.CANONICAL_SCHEMA.items():
                if any(keyword in normalized for keyword in keywords):
                    if canonical not in self.mapping:
                        self.mapping[canonical] = column

        return self.mapping
