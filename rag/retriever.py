class SchemaRetriever:
    """
    Deterministic schema-based retriever.
    No embeddings, no vector store.
    """

    def __init__(self, schema: dict):
        self.schema = schema

    def invoke(self, query: str):
        query_lower = query.lower()
        results = []

        for canonical, column in self.schema.items():
            if canonical in query_lower or column.lower() in query_lower:
                results.append(
                    f"Business Concept: {canonical}\n"
                    f"Dataset Column: {column}\n"
                    f"Description: This column represents '{canonical}' "
                    f"in the dataset and is used for analysis."
                )

        if not results:
            results.append("No additional contextual information available.")

        return results
