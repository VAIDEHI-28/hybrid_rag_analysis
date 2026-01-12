from ingestion.registry import DataRegistry
from schema.schema_mapper import SchemaMapper
from schema.schema_store import SchemaStore


class SchemaService:
    """
    Orchestrates schema inference and storage for ingested data.
    """

    def __init__(self, registry: DataRegistry):
        self.registry = registry
        self.schema_store = SchemaStore()

    def infer_and_store_schema(self) -> dict:
        all_data = self.registry.get_all_sheets()

        if not all_data:
            raise ValueError("No data available in registry for schema inference.")

        first_file = next(iter(all_data))
        first_sheet = next(iter(all_data[first_file]))

        dataframe = all_data[first_file][first_sheet]

        mapper = SchemaMapper(dataframe)
        schema = mapper.infer()

        self.schema_store.save(schema)
        return schema

    def get_schema(self) -> dict:
        return self.schema_store.get()
