from pathlib import Path

from config import OUTPUT_DIR

# from utils.json_utils import JsonUtils

import re
import unicodedata


class CleaningAgent:

    @staticmethod
    def run(document):

        markdown = document.markdown

        ####################################################
        # Unicode normalization
        ####################################################

        markdown = unicodedata.normalize("NFKC", markdown)

        ####################################################
        # Remove invisible characters
        ####################################################

        markdown = markdown.replace("\u200b", "")
        markdown = markdown.replace("\ufeff", "")
        markdown = markdown.replace("\u00a0", " ")

        ####################################################
        # Normalize line endings
        ####################################################

        markdown = markdown.replace("\r\n", "\n")
        markdown = markdown.replace("\r", "\n")

        ####################################################
        # Remove trailing whitespace
        ####################################################

        markdown = "\n".join(line.rstrip() for line in markdown.splitlines())

        ####################################################
        # Collapse excessive blank lines
        ####################################################

        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        ####################################################
        # Remove Marker page separators
        ####################################################

        markdown = re.sub(
            r"\n-{20,}\n",
            "\n",
            markdown,
        )

        ####################################################
        # Final cleanup
        ####################################################

        markdown = markdown.strip()

        document.cleaned_markdown = markdown

        ####################################################
        # Save cleaned markdown
        ####################################################

        output_folder = OUTPUT_DIR / Path(document.filepath).stem

        cleaned_folder = output_folder / "cleaned"

        cleaned_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        cleaned_file = cleaned_folder / "cleaned_markdown.md"

        cleaned_file.write_text(
            markdown,
            encoding="utf-8",
        )

        ####################################################
        # Update extracted document json
        ####################################################

        # JsonUtils.save(
        #     document,
        #     output_folder / "extracted_document.json",
        # )

        ####################################################
        # Console
        ####################################################

        print()
        print("=" * 70)
        print("CLEANING COMPLETED")
        print("=" * 70)
        print(f"Characters : {len(markdown):,}")
        print("=" * 70)
        print()

        return document
