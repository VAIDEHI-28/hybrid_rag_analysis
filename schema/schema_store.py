from typing import Dict


class SchemaStore:
    """
    Stores semantic schema for the current dataset.
    """

    def __init__(self):
        self._schema: Dict[str, str] = {}

    def save(self, schema: Dict[str, str]):
        self._schema = schema

    def get(self) -> Dict[str, str]:
        return self._schema

    def has(self, key: str) -> bool:
        return key in self._schema
