import json
import re
from llm.orchestrator import get_llm
from planner.planner_prompt import PLANNER_PROMPT


class AnalyticsPlanner:
    def __init__(self, schema: dict):
        self.schema = schema
        self.llm = get_llm()

    # ------------------------------------------------
    def plan(self, question: str) -> dict:
        """
        Generate a schema-safe execution plan.
        This planner NEVER allows hallucinated columns.
        """

        # Create hard-locked schema list
        schema_keys = list(self.schema.keys())
        schema_description = "\n".join([f"- {k}" for k in schema_keys])

        prompt = PLANNER_PROMPT.format(schema=schema_description)

        response = self.llm.invoke(
            prompt + f"\n\nQuestion: {question}\nOutput:"
        )

        raw = response.content.strip()

        print("\n===== PLANNER DEBUG =====")
        print(raw)
        print("=========================\n")

        # Remove ```json wrappers if model adds them
        raw = re.sub(r"```json|```", "", raw).strip()

        try:
            plan = json.loads(raw)
        except Exception:
            return {"operation": "unsupported"}

        # ---- Strict validation against schema ----
        def validate_step(step):
            for key in ["column", "metric", "group_by", "list_column"]:
                if key in step and step[key] not in self.schema:
                    return False

            if "filters" in step:
                for f in step["filters"]:
                    if f not in self.schema:
                        return False

            return True

        # Multi-step
        if "steps" in plan:
            for s in plan["steps"]:
                if not validate_step(s):
                    return {"operation": "unsupported"}
            return plan

        # Single-step
        if not validate_step(plan):
            return {"operation": "unsupported"}

        return plan
