from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from ingestion.registry import DataRegistry
from ingestion.loader import load_excel_file
from ingestion.validator import validate_excel_files
from chains.hybrid_chain import HybridRAGChain


def main():
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

    data = registry.get_all_sheets()
    file = next(iter(data))
    sheet = next(iter(data[file]))
    df = data[file][sheet]

    import uuid
    session_id = str(uuid.uuid4())

    chain = HybridRAGChain(df, registry, session_id)


    print("\n🧠 Hybrid RAG Analytics Chatbot Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ")
        if question.lower() == "exit":
            break

        answer = chain.run(question)
        print("\nAnswer:\n", answer, "\n")


if __name__ == "__main__":
    main()
