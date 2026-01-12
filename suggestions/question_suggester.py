from llm.orchestrator import get_llm


class QuestionSuggester:
    def __init__(self, schema: dict):
        self.schema = schema
        self.llm = get_llm()

    def suggest(self, last_plan: dict):
        if not last_plan:
            return []

        prompt = f"""
You are a data analyst assistant.

Suggest exactly 3 useful follow-up analytical questions
based on the last user intent.

Rules:
- Use ONLY the available columns
- Do NOT invent data
- Do NOT mention values
- Do NOT repeat the same question
- Return ONLY bullet points

Available columns:
{", ".join(self.schema.keys())}

Last analytical intent:
{last_plan}

Format:
• question 1
• question 2
• question 3
"""

        response = self.llm.invoke(prompt)

        # Convert bullets into a clean list
        lines = response.content.strip().split("\n")
        return [line.replace("•", "").strip() for line in lines if line.strip()]
