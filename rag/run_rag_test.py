from dotenv import load_dotenv
load_dotenv()

from ingestion.registry import DataRegistry
from ingestion.loader import load_excel_file
from ingestion.validator import validate_excel_files
from schema.schema_service import SchemaService
from rag.documents import build_rag_documents
from rag.embeddings import get_embeddings
from rag.vectorstore import build_vectorstore
from rag.retriever import get_retriever
from pathlib import Path


def run_rag_test():
    registry = DataRegistry()

    upload_dir = Path("data/uploads")
    excel_files = list(upload_dir.glob("*.xlsx"))

    validate_excel_files(excel_files)

    for file_path in excel_files:
        sheets = load_excel_file(file_path)
        for sheet_name, df in sheets.items():
            registry.register_sheet(
                file_name=file_path.name,
                sheet_name=sheet_name,
                dataframe=df
            )

    schema_service = SchemaService(registry)
    schema = schema_service.infer_and_store_schema()

    documents = build_rag_documents(schema)
    embeddings = get_embeddings()
    vectorstore = build_vectorstore(documents, embeddings)
    retriever = get_retriever(vectorstore)

    results = retriever.invoke("Explain Quality Rating")

    print("\nRAG Results:")
    for doc in results:
        print("-", doc.page_content)


if __name__ == "__main__":
    run_rag_test()
