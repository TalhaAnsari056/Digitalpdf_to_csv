from pathlib import Path

from config import OUTPUT_DIR
from models.document import Document
from services.marker_service import MarkerService
from utils.json_utils import JsonUtils


class ExtractionAgent:

    @staticmethod
    def run(pdf_path: Path):

        output_folder = OUTPUT_DIR / pdf_path.stem
        output_folder.mkdir(parents=True, exist_ok=True)

        ####################################################
        # Marker Extraction
        ####################################################

        marker_output = MarkerService.extract(
            pdf_path=pdf_path,
            output_dir=output_folder,
        )

        ####################################################
        # Find generated markdown
        ####################################################

        markdown_files = list(marker_output.rglob("*.md"))

        if not markdown_files:
            raise RuntimeError("Marker did not generate any markdown file.")

        markdown_file = markdown_files[0]

        markdown = markdown_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        ####################################################
        # Build Document object
        ####################################################

        document = Document(
            filename=pdf_path.name,
            filepath=str(pdf_path),
            markdown_path=str(markdown_file),
            markdown=markdown,
        )

        ####################################################
        # Save debugging copy
        ####################################################

        extraction_folder = output_folder / "extraction"
        extraction_folder.mkdir(parents=True, exist_ok=True)

        debug_md = extraction_folder / "raw_marker_output.md"

        debug_md.write_text(
            markdown,
            encoding="utf-8",
        )

        ####################################################
        # Save Document JSON
        ####################################################

        JsonUtils.save(
            document,
            output_folder / "extracted_document.json",
        )

        ####################################################
        # Console Output
        ####################################################

        print()
        print("=" * 70)
        print("MARKER EXTRACTION COMPLETED")
        print("=" * 70)
        print(f"Markdown file : {markdown_file.name}")
        print(f"Characters    : {len(markdown):,}")
        print("=" * 70)
        print()

        return document
