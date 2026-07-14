from pathlib import Path
import time

from docling.document_converter import DocumentConverter

PROJECT_ROOT = Path(__file__).resolve().parent.parent

pdf = PROJECT_ROOT / "input" / "pdfs" / "Balance-Sheet-Example_digitalPDF.pdf"

output_dir = PROJECT_ROOT / "output" / "docling_test"
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("DOCILING TEST")
print("=" * 60)

start = time.perf_counter()

converter = DocumentConverter()

result = converter.convert(str(pdf))

elapsed = time.perf_counter() - start

document = result.document

# -----------------------
# Markdown
# -----------------------

markdown = document.export_to_markdown()

(output_dir / "out.md").write_text(markdown, encoding="utf-8")

# -----------------------
# JSON
# -----------------------

json_text = document.export_to_dict()

import json

with open(output_dir / "out.json", "w", encoding="utf-8") as f:
    json.dump(
        json_text,
        f,
        indent=2,
        ensure_ascii=False,
    )

print()

print("Finished Successfully")

print(f"Execution Time : {elapsed:.2f} sec")
print(f"Characters     : {len(markdown)}")
print(f"Words          : {len(markdown.split())}")

print()

print("Output Folder")

print(output_dir)
