import json
from pathlib import Path


class JsonUtils:

    @staticmethod
    def save(document, output_path: Path):

        data = {
            "filename": document.filename,
            "filepath": document.filepath,
            "document_type": document.document_type,
            "pages": [],
        }

        for page in document.pages:

            page_data = {
                "page_number": page.page_number,
                "text": page.text,
                "words": [],
            }

            for word in page.words:

                page_data["words"].append(
                    {
                        "text": word.text,
                        "x0": word.x0,
                        "y0": word.y0,
                        "x1": word.x1,
                        "y1": word.y1,
                        "block_no": word.block_no,
                        "line_no": word.line_no,
                        "word_no": word.word_no,
                    }
                )

            data["pages"].append(page_data)

        with open(output_path, "w", encoding="utf-8") as file:

            json.dump(data, file, indent=4, ensure_ascii=False)
