import json
from pathlib import Path


class JsonUtils:

    @staticmethod
    def save(document, output_path: Path):

        data = {
            "filename": document.filename,
            "filepath": document.filepath,
            "markdown_path": document.markdown_path,
            "document_type": document.document_type,
            "cleaned_markdown": document.cleaned_markdown,
            "mapped_json": document.mapped_json,
            "validation_report": document.validation_report,
            "csv_path": document.csv_path,
        }

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )
