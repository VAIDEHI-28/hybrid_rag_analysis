import json
import re
from llm.orchestrator import get_llm
from planner.planner_prompt import PLANNER_PROMPT


class AnalyticsPlanner:
    def __init__(self, schema: dict):
        self.schema = schema
        self.llm = get_llm()

    # ---------------------------
    # Time parser (deterministic)
    # ---------------------------
    def extract_time_range(self, question: str):
        q = question.lower()

        if "last 6 months" in q:
            return "last 6 months"
        if "last 3 months" in q or "last quarter" in q:
            return "last 3 months"
        if "last year" in q:
            return "last year"
        if "this year" in q:
            return "this year"

        match = re.search(r"\b(20\d{2})\b", q)
        if match:
            return match.group(1)

        return None

    # ---------------------------
    # Planner
    # ---------------------------
    def plan(self, question: str) -> dict:
        schema_description = "\n".join(
            [f"{k} → {v}" for k, v in self.schema.items()]
        )

        prompt = PLANNER_PROMPT.format(schema=schema_description)

        response = self.llm.invoke(
            prompt + f"\nQuestion: {question}\nOutput:"
        )

        raw = response.content.strip()

        # 🔥 CRITICAL FIX: Remove markdown fences if LLM returned ```json
        raw = raw.replace("```json", "").replace("```", "").strip()

        print("\n===== PLANNER DEBUG =====")
        print(raw)
        print("=========================\n")

        try:
            plan = json.loads(raw)
        except Exception as e:
            print("❌ Planner JSON parse failed:", e)
            return {"operation": "unsupported"}

        # Attach time if detected
        time_range = self.extract_time_range(question)
        if time_range:
            if "steps" in plan:
                for step in plan["steps"]:
                    step["time_range"] = time_range
            else:
                plan["time_range"] = time_range

        return plan
