ALLOWED_OPERATIONS = {
    "sum",
    "mean",
    "min",
    "max",
    "count_unique",
    "list_unique",
    "top_k_sum",
    "top_k_count",
}


class PlanValidator:
    def __init__(self, schema: dict):
        self.schema = schema

    def validate(self, plan: dict):
        if plan["operation"] not in ALLOWED_OPERATIONS:
            raise ValueError("Invalid operation requested")

        if plan["metric"] not in self.schema:
            raise ValueError("Invalid metric column")

        if plan.get("group_by") and plan["group_by"] not in self.schema:
            raise ValueError("Invalid group_by column")

        for key in plan.get("filters", {}).keys():
            if key not in self.schema:
                raise ValueError("Invalid filter column")

        return True
