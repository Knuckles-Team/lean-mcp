"""Declared data sources: typed data the SDK reads with `load_declaration`."""

from scion_sdk.ingest.live_declaration import source_meta

SCHEMA_VERSION = 1

SOURCES = (
    source_meta(
        tool="lean_extract",
        source_id="lean_declarations",
        record_type="LeanDeclaration",
        id_field="name",
        ontology_class="Declaration",
        records_path="declarations",
        fields={"kind": "kind", "module": "module"},
    ),
)
