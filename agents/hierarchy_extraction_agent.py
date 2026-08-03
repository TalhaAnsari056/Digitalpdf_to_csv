from pathlib import Path

from config import OUTPUT_DIR
from services.hierarchy_extraction_service import HierarchyExtractionService


class HierarchyExtractionAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("HIERARCHY EXTRACTION")
        print("=" * 70)

        ############################################################
        # Orchestration only
        ############################################################

        document = HierarchyExtractionService.process(document)

        ############################################################
        # Terminal Summary
        ############################################################

        print("\nHierarchy Extraction Summary")
        print("-" * 40)
        print(f"Document             : {document.filename}")
        print(
            f"Hierarchy Prompt     : {Path(document.hierarchy_prompt_path).name if document.hierarchy_prompt_path else 'N/A'}"
        )
        print(
            f"Raw Response         : {Path(document.raw_hierarchy_response_path).name if document.raw_hierarchy_response_path else 'N/A'}"
        )
        print(
            f"Hierarchy File       : {Path(document.hierarchy_path).name if document.hierarchy_path else 'N/A'}"
        )
        print(
            f"Extraction Report    : {Path(document.extraction_report_path).name if document.extraction_report_path else 'N/A'}"
        )

        print("\nHierarchy Extraction completed successfully.")
        print("=" * 70)

        return document
