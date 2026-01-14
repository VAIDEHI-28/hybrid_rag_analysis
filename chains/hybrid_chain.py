import json
from planner.analytics_planner import AnalyticsPlanner
from tools.pandas_tool import PandasAnalyticsTool

class HybridRAGChain:
    def __init__(self, df, schema, session_id):
        self.planner = AnalyticsPlanner(schema)
        self.tool = PandasAnalyticsTool(df, schema)

    def run(self, question):
        raw = self.planner.plan(question)
        plan = json.loads(raw) if isinstance(raw, str) else raw

        try:
            return self.tool.run(plan)
        except Exception as e:
            return f"❌ Pandas error: {e}"
