from config import OUTPUT_DIR
from services.pdf_service import PDFService
from utils.json_utils import JsonUtils
from services.layout_reconstruction_service import LayoutReconstructionService


class ExtractionAgent:

    @staticmethod
    def run(pdf_path):

        document = PDFService.extract(pdf_path)

        rows = LayoutReconstructionService.reconstruct(document)

        # Save reconstructed layout into the document
        document.rows = rows

        print("\n===== RECONSTRUCTED ROWS =====\n")

        for row in rows[:80]:
            print(row.text)

        output_folder = OUTPUT_DIR / pdf_path.stem

        layout_folder = output_folder / "layout"

        layout_folder.mkdir(parents=True, exist_ok=True)

        extraction_folder = output_folder / "extraction"

        extraction_folder.mkdir(parents=True, exist_ok=True)

        layout_file = layout_folder / "reconstructed_rows.txt"

        with open(layout_file, "w", encoding="utf-8") as file:

            for row in rows:

                file.write(f"[Page {row.page_number}] ")

                file.write(row.text)

                file.write("\n")

        for page in document.pages:

            page_file = extraction_folder / f"page_{page.page_number:03}.txt"

            with open(page_file, "w", encoding="utf-8") as file:

                file.write(page.text)

            print(f"Page {page.page_number}: {len(page.words)} words extracted")

        json_path = output_folder / "extracted_document.json"

        JsonUtils.save(document, json_path)

        return document
