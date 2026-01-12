from llm.orchestrator import get_llm


class OutputFormatter:
    """
    Converts raw analytical results into clean, human-friendly answers.
    LLM is ONLY allowed to format, not compute.
    """

    def __init__(self):
        self.llm = get_llm()

    def format(self, question: str, result):
        """
        Takes:
            - question (user input)
            - result (raw pandas output)
        Returns:
            - clean human answer
        """

        # If data is missing, never hallucinate
        if result in ["Data not available", None, {}, [], ["Data not available"]]:
            return "Data not available."

        prompt = f"""
You are a business analyst assistant.

Your job is ONLY to format the data below into a clear,
professional, human-readable answer.

STRICT RULES:
• Do NOT perform calculations
• Do NOT change numbers
• Do NOT add new facts
• Do NOT guess
• Only rewrite what is provided

User question:
{question}

Raw result:
{result}

Now present this result in bullet points or short paragraphs,
like ChatGPT would do for a business user.
"""

        response = self.llm.invoke(prompt)
        return response.content.strip()
