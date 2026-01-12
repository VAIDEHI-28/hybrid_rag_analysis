from typing import List
from langchain_core.documents import Document


def build_rag_documents(schema: dict) -> List[Document]:
    """
    Build contextual RAG documents from schema and business metadata.
    """
    docs = []

    for canonical, column in schema.items():
        content = f"""
        Business Concept: {canonical}

        Dataset Column: {column}

        Description:
        This column represents '{canonical}' in the dataset.
        It is used for analytical breakdowns, grouping, filtering,
        and interpretation of supply chain performance.
        """

        docs.append(
            Document(
                page_content=content.strip(),
                metadata={"type": "schema", "concept": canonical}
            )
        )

    return docs
