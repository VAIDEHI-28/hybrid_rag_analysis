import json
import os
import hashlib
import pandas as pd

# Cache will live next to this file
BASE_DIR = os.path.dirname(__file__)
SCHEMA_CACHE_PATH = os.path.join(BASE_DIR, "schema_cache.json")


def dataframe_fingerprint(df: pd.DataFrame) -> str:
    """
    Creates a unique fingerprint for the dataframe
    based on columns + row count.
    If Excel changes → fingerprint changes → schema rebuilds.
    """
    signature = "|".join(df.columns) + f"|{len(df)}"
    return hashlib.md5(signature.encode()).hexdigest()


def normalize(col_name: str) -> str:
    """
    Convert column names into planner-safe semantic keys
    """
    return (
        col_name.lower()
        .strip()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
    )


def build_schema(df: pd.DataFrame) -> dict:
    """
    Build semantic schema directly from dataframe
    This is the single source of truth.
    """
    schema = {}
    for col in df.columns:
        semantic_key = normalize(col)
        schema[semantic_key] = col
    return schema


def load_cached_schema():
    if not os.path.exists(SCHEMA_CACHE_PATH):
        return None

    with open(SCHEMA_CACHE_PATH, "r") as f:
        return json.load(f)


def save_schema(schema: dict, fingerprint: str):
    with open(SCHEMA_CACHE_PATH, "w") as f:
        json.dump(
            {
                "fingerprint": fingerprint,
                "schema": schema
            },
            f,
            indent=2
        )


def get_semantic_schema(df: pd.DataFrame) -> dict:
    """
    Enterprise-grade schema loader.
    Schema is reused ONLY if dataframe is identical.
    """
    fingerprint = dataframe_fingerprint(df)
    cached = load_cached_schema()

    if cached:
        if cached.get("fingerprint") == fingerprint:
            print("🔁 Using cached semantic schema")
            return cached["schema"]
        else:
            print("♻️ Data changed → rebuilding semantic schema")

    print("🧠 Building semantic schema from DataFrame")
    schema = build_schema(df)
    save_schema(schema, fingerprint)
    return schema
