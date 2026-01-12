from typing import Dict


class ToolRouter:
    """
    Decides which tool(s) to use based on user question intent.
    """

    ANALYTICAL_KEYWORDS = [
        "total", "sum", "highest", "lowest", "top", "maximum", "minimum",
        "count", "average", "mean", "cost", "spend", "price"
    ]

    CONTEXTUAL_KEYWORDS = [
        "what is", "define", "explain", "meaning", "why"
    ]

    def route(self, question: str) -> Dict[str, bool]:
        question_lower = question.lower()

        needs_analytics = any(
            keyword in question_lower for keyword in self.ANALYTICAL_KEYWORDS
        )

        needs_context = any(
            keyword in question_lower for keyword in self.CONTEXTUAL_KEYWORDS
        )

        return {
            "use_pandas": needs_analytics,
            "use_rag": needs_context
        }
