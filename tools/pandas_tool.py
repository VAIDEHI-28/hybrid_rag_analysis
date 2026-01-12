import pandas as pd
from typing import Dict


class PandasAnalyticsTool:
    def __init__(self, dataframe: pd.DataFrame, schema: Dict[str, str]):
        self.df = dataframe
        self.schema = schema

        # Semantic aliases (LLM → dataframe)
        self.aliases = {
            "vendor": "vendor_name",
            "product": "product_name",
            "plant": "plant_name",
            "material": "material",
            "category": "category",
            "cost": "cost",
            "quality": "quality",
            "region": "region",
        }

    # ----------------------------
    def _resolve_key(self, key):
        # map LLM word → canonical schema key
        key = key.lower().strip()
        if key in self.schema:
            return key
        if key in self.aliases and self.aliases[key] in self.schema:
            return self.aliases[key]
        raise ValueError(f"Unknown column: {key}")

    def _get_column(self, key):
        resolved = self._resolve_key(key)
        return self.schema[resolved]

    def _apply_filters(self, df, filters):
        if not filters:
            return df

        for key, value in filters.items():
            col = self._get_column(key)

        # fuzzy match instead of ==
        df = df[
            df[col]
            .astype(str)
            .str.lower()
            .str.contains(str(value).lower(), na=False)
        ]

        return df


    # ----------------------------
    def count_unique(self, column, filters=None):
        df = self._apply_filters(self.df, filters)
        col = self._get_column(column)
        return int(df[col].nunique())

    def list_unique(self, column, filters=None):
        df = self._apply_filters(self.df, filters)
        col = self._get_column(column)
        return sorted(df[col].dropna().unique().tolist())

    def aggregate(self, metric, operation, group_by=None, filters=None):
        df = self._apply_filters(self.df, filters)
        metric_col = self._get_column(metric)

        if group_by:
            group_col = self._get_column(group_by)
            return df.groupby(group_col)[metric_col].agg(operation).to_dict()

        return getattr(df[metric_col], operation)()

    def top_k(self, metric, group_by, k=1, filters=None):
        df = self._apply_filters(self.df, filters)
        m = self._get_column(metric)
        g = self._get_column(group_by)
        return df.groupby(g)[m].sum().sort_values(ascending=False).head(k).to_dict()

    def group_list(self, group_by, list_column, filters=None):
        df = self._apply_filters(self.df, filters)
        g = self._get_column(group_by)
        l = self._get_column(list_column)
        return df.groupby(g)[l].unique().apply(list).to_dict()
