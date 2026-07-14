from pathlib import Path
import subprocess


class MarkerService:

    @staticmethod
    def extract(pdf_path: Path, output_dir: Path):

        markdown_dir = output_dir / "markdown"
        markdown_dir.mkdir(parents=True, exist_ok=True)

        command = [
            "marker_single",
            str(pdf_path),
            "--output_dir",
            str(markdown_dir),
            # ======================================================
            # OCR CONFIGURATION
            # ======================================================
            # ---------- OCR ENABLED (Default) ----------
            # (leave these commented)
            # ---------- OCR DISABLED (Digital PDFs) ----------
            "--DocumentBuilder_disable_ocr",
            "--LineBuilder_disable_ocr",
            "--TableProcessor_disable_ocr",
            # ======================================================
        ]

        print("Running Marker:")
        print(" ".join(command))

        result = subprocess.run(
            command,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError("Marker extraction failed.")

        return markdown_dir
