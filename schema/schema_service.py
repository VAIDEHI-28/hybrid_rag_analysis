import json
from pathlib import Path
from schema.semantic_schema import SemanticSchemaEngine


class SchemaService:
    """
    Controls semantic schema inference + caching.
    Ensures we NEVER re-call Gemini unless required.
    """

    def __init__(self, df):
        self.df = df
        self.cache_path = Path("schema_cache.json")

    def infer_and_store_schema(self):
        """
        Returns a valid semantic schema:
        {
            "vendor": "Vendor Name",
            "product": "Product Name",
            "cost": "Cost",
            ...
        }
        """

        # 1️⃣ Load from cache if valid
        if self.cache_path.exists():
            try:
                cached = json.loads(self.cache_path.read_text())
                if isinstance(cached, dict) and len(cached) > 0:
                    print("🔁 Loaded schema from cache")
                    return cached
            except:
                pass  # corrupted cache → regenerate

        # 2️⃣ Infer via LLM
        engine = SemanticSchemaEngine(self.df)
        schema = engine.infer()

        # 3️⃣ Validate schema against dataframe
        clean_schema = {}
        for semantic, original in schema.items():
            if original in self.df.columns:
                clean_schema[semantic] = original

        if not clean_schema:
            raise ValueError("❌ Semantic schema inference failed — no valid columns mapped.")

        # 4️⃣ Save to cache
        self.cache_path.write_text(json.dumps(clean_schema, indent=2))

        return clean_schema
