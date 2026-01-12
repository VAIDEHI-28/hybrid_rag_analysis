from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Ensure environment variables are loaded
load_dotenv()


def create_llm():
    """
    Create and return a Gemini LLM instance.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY not found. "
            "Ensure .env exists at project root and is loaded."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )
