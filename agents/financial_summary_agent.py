from pathlib import Path

from config import OUTPUT_DIR
from services.financial_summary_service import FinancialSummaryService


class FinancialSummaryAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("FINANCIAL SUMMARY EXTRACTION")
        print("=" * 70)

        ############################################################
        # Orchestration only
        ############################################################

        document = FinancialSummaryService.process(document)

        ############################################################
        # Terminal Summary
        ############################################################

        print("\nFinancial Summary Summary")
        print("-" * 40)
        print(f"Document              : {document.filename}")
        print(
            f"Prompt File            : {Path(document.financial_summary_prompt_path).name if document.financial_summary_prompt_path else 'N/A'}"
        )
        print(
            f"Raw Response File      : {Path(document.raw_financial_summary_response_path).name if document.raw_financial_summary_response_path else 'N/A'}"
        )
        print(
            f"Summary File           : {Path(document.financial_summary_path).name if document.financial_summary_path else 'N/A'}"
        )
        print(
            f"Summary Report File    : {Path(document.financial_summary_report_path).name if document.financial_summary_report_path else 'N/A'}"
        )

        print("\nFinancial Summary Extraction completed successfully.")
        print("=" * 70)

        return document
