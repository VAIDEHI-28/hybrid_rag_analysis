from llm.model import create_llm


def get_llm():
    """
    Public accessor used by chains.
    """
    return create_llm()
