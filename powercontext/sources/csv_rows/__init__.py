from typing import Tuple, Any
from pydantic import BaseModel
from powercontext.source import Source, SourceDefinition
from powercontext.text_evidence import TextEvidence
import csv
import io
import urllib.parse
import json


class CSVDocumentInput(BaseModel):
    document_id: str
    primary_key: str
    content: bytes


class CSVRowInput(BaseModel):
    document_id: str
    primary_key: str
    columns: Tuple[str, ...]
    values: Tuple[Any, ...]


class CSVRowSource(Source):
    @staticmethod
    def parse(input_data: CSVDocumentInput) -> Tuple[CSVRowInput, ...]:
        result = []
        content_str = input_data.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content_str))
        rows = list(reader)
        if len(rows) == 0:
            return tuple(result)
        header = rows[0]
        pk_index = header.index(input_data.primary_key)

        for r in rows[1:]:
            if len(r) != len(header):
                raise ValueError("Column count mismatch between header and row")
            pk_val = r[pk_index]
            if pk_val == "":
                raise ValueError("Primary key value is empty string")

            row_in = CSVRowInput(
                document_id=input_data.document_id,
                primary_key=pk_val,
                columns=tuple(header),
                values=tuple(r)
            )
            result.append(row_in)
        return tuple(result)


CSV_ROW_SOURCE_DEFINITION: SourceDefinition[CSVDocumentInput, CSVRowSource, CSVRowInput] = SourceDefinition(
    name="csv-row",
    version=1,
    input_class=CSVDocumentInput,
    source_class=CSVRowSource
)

from powercontext.source.registry import SourceDefinitionRegistry
SourceDefinitionRegistry.register(CSV_ROW_SOURCE_DEFINITION)
