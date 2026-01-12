from planner.analytics_planner import AnalyticsPlanner
from tools.pandas_tool import PandasAnalyticsTool
from llm.orchestrator import get_llm
from memory.context_memory import ContextMemory
from formatting.output_formatter import OutputFormatter


class HybridRAGChain:
    """
    Enterprise-grade Hybrid RAG Engine

    LLM → Planner → Pandas → Formatter → User
    """

    def __init__(self, dataframe, registry, session_id):
        self.df = dataframe
        self.registry = registry
        self.session_id = session_id

        # Build semantic schema dynamically from dataframe
        self.schema = self._build_schema_from_df(dataframe)

        self.planner = AnalyticsPlanner(self.schema)
        self.tool = PandasAnalyticsTool(self.df, self.schema)
        self.llm = get_llm()
        self.memory = ContextMemory(session_id)
        self.formatter = OutputFormatter()

    # -------------------------------------------------
    # Dynamic semantic schema
    # -------------------------------------------------
    def _build_schema_from_df(self, df):
        """
        Builds canonical keys from column names.
        Example:
            'Vendor Name' → 'vendor_name'
            'Plant' → 'plant'
        """
        schema = {}
        for col in df.columns:
            key = col.lower().strip().replace(" ", "_")
            schema[key] = col
        return schema

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------
    def run(self, question: str):
        """
        Main execution pipeline
        """

        # Resolve follow-ups using memory
        resolved = self.memory.resolve_followup(question)

        # Get analytical plan
        plan = self.planner.plan(resolved)

        # Stop safely if unsupported
        if not plan or plan.get("operation") == "unsupported":
            return "Data not available."

        # Store intent only (never results)
        self.memory.update(plan)

        # Execute
        try:
            # Multi-step
            if "steps" in plan:
                raw_results = []
                for step in plan["steps"]:
                    raw_results.append(self._execute(step))

                return self.formatter.format(question, raw_results)

            # Single-step
            raw = self._execute(plan)

            # Optional explanation
            if plan.get("explanation_required") and raw != "Data not available":
                explanation = self._explain(raw)
                return explanation

            return self.formatter.format(question, raw)

        except Exception:
            return "Data not available."

    # -------------------------------------------------
    # Pandas execution engine
    # -------------------------------------------------
    def _execute(self, step):
        try:
            op = step.get("operation")

            if op == "count_unique":
                return self.tool.count_unique(step["column"], step.get("filters"))

            if op == "list_unique":
                return self.tool.list_unique(step["column"], step.get("filters"))

            if op == "aggregate":
                return self.tool.aggregate(
                    step["metric"],
                    step["function"],
                    step.get("group_by"),
                    step.get("filters"),
                )

            if op == "top_k":
                return self.tool.top_k(
                    step["metric"],
                    step["group_by"],
                    step.get("k", 1),
                    step.get("filters"),
                )

            if op == "group_list":
                return self.tool.group_list(
                    step["group_by"],
                    step["list_column"],
                    step.get("filters"),
                )

        except Exception:
            return "Data not available"

        return "Data not available"

    # -------------------------------------------------
    # Safe LLM explanation
    # -------------------------------------------------
    def _explain(self, result):
        prompt = f"""
You are a business analyst.

Explain this result clearly.
Do NOT change numbers.
Do NOT invent data.

Result:
{result}
"""
        return self.llm.invoke(prompt).content.strip()
