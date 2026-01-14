class PandasAnalyticsTool:
    def __init__(self, df, schema):
        self.df = df
        self.schema = schema

    def run(self, plan):
        op = plan["operation"].strip().lower()

        def col(x):
            return self.schema[x]

        df = self.df

        # Apply filters
        for k, v in (plan.get("filters") or {}).items():
            df = df[df[col(k)].astype(str).str.lower() == str(v).lower()]

        # Execute
        if op == "count_unique":
            return int(df[col(plan["column"])].nunique())

        if op == "list_unique":
            return df[col(plan["column"])].dropna().unique().tolist()

        if op == "aggregate":
            m = col(plan["metric"])
            f = plan["function"].strip().lower()

            if f == "max": return df[m].max()
            if f == "min": return df[m].min()
            if f == "sum": return df[m].sum()
            if f == "avg": return round(df[m].mean(), 2)

        raise ValueError(f"Unknown operation: {op}")
