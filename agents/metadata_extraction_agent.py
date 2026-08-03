from pathlib import Path

from config import OUTPUT_DIR
from services.metadata_extraction_service import MetadataExtractionService


class MetadataExtractionAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("METADATA EXTRACTION")
        print("=" * 70)

        ############################################################
        # Orchestration only
        ############################################################

        document = MetadataExtractionService.process(document)

        ############################################################
        # Terminal Summary
        ############################################################

        print("\nMetadata Extraction Summary")
        print("-" * 40)
        print(f"Document            : {document.filename}")
        print(
            f"Metadata Prompt     : {Path(document.metadata_prompt_path).name if document.metadata_prompt_path else 'N/A'}"
        )
        print(
            f"Raw Response        : {Path(document.raw_metadata_response_path).name if document.raw_metadata_response_path else 'N/A'}"
        )
        print(
            f"Metadata File       : {Path(document.metadata_path).name if document.metadata_path else 'N/A'}"
        )
        print(
            f"Extraction Report   : {Path(document.extraction_report_path).name if document.extraction_report_path else 'N/A'}"
        )

        print("\nMetadata Extraction completed successfully.")
        print("=" * 70)

        return document
