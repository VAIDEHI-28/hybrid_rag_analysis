from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import uuid
import pandas as pd

from ingestion.registry import DataRegistry
from ingestion.loader import load_excel_file
from ingestion.validator import validate_excel_files
from chains.hybrid_chain import HybridRAGChain
from schema.semantic_schema import get_semantic_schema   # ✅ correct import


def main():
    print("\n🚀 Starting Hybrid RAG Engine...\n")

    # ----------------------------
    # 1️⃣ Load Excel files
    # ----------------------------
    registry = DataRegistry()
    upload_dir = Path("data/uploads")

    excel_files = list(upload_dir.glob("*.xlsx"))

    if not excel_files:
        print("❌ No Excel files found in data/uploads")
        print("➡ Please upload at least one Excel file and restart.")
        return

    validate_excel_files(excel_files)

    print(f"📂 Loading {len(excel_files)} Excel file(s)...")

    for file_path in excel_files:
        print(f"  - {file_path.name}")
        sheets = load_excel_file(file_path)
        for sheet_name, df in sheets.items():
            registry.register_sheet(
                file_name=file_path.name,
                sheet_name=sheet_name,
                dataframe=df
            )

    # ----------------------------
    # 2️⃣ Merge all sheets
    # ----------------------------
    data = registry.get_all_sheets()
    all_frames = []

    for file in data:
        for sheet in data[file]:
            df = data[file][sheet]
            if not df.empty:
                all_frames.append(df)

    if not all_frames:
        print("\n❌ ERROR: All Excel sheets are empty.")
        return

    df = pd.concat(all_frames, ignore_index=True)

    print("\n📊 DATAFRAME LOADED")
    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    print(df.head())

    print("\n🧪 SANITY CHECK")
    print("Unique vendors:", df["Vendor Name"].nunique())
    print("Unique regions:", df["Region"].nunique())
    print("First 5 vendors:", df["Vendor Name"].head().tolist())

    if len(df) == 0:
        print("\n❌ ERROR: DataFrame is empty after merging.")
        return

    # ----------------------------
    # 3️⃣ Session ID
    # ----------------------------
    session_id = str(uuid.uuid4())

    # ----------------------------
    # 4️⃣ Semantic Schema (FIXED)
    # ----------------------------
    print("\n🧠 Inferring semantic schema...")
    schema = get_semantic_schema(df)     # ✅ ONLY source of truth

    print("\n🧠 Active Semantic Schema:")
    for k, v in schema.items():
        print(f"  {k} → {v}")

    # ----------------------------
    # 5️⃣ Create Hybrid RAG Chain
    # ----------------------------
    chain = HybridRAGChain(df, schema, session_id)

    # ----------------------------
    # 6️⃣ CLI Loop
    # ----------------------------
    print("\n🧠 Hybrid RAG Analytics Chatbot Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ").strip()

        if question.lower() == "exit":
            print("👋 Session ended.")
            break

        try:
            answer = chain.run(question)
        except Exception as e:
            answer = f"❌ Error: {str(e)}"

        print("\nAnswer:\n", answer, "\n")


if __name__ == "__main__":
    main()
