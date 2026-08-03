from pathlib import Path

from config import OUTPUT_DIR
from services.financial_analytics_service import FinancialAnalyticsService


class FinancialAnalyticsAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("FINANCIAL ANALYTICS")
        print("=" * 70)

        ############################################################
        # Orchestration only
        ############################################################

        document = FinancialAnalyticsService.process(document)

        ############################################################
        # Terminal Summary
        ############################################################

        print("\nFinancial Analytics Summary")
        print("-" * 40)
        print(f"Document              : {document.filename}")
        print(
            f"Analytics File        : {Path(document.financial_analytics_path).name if document.financial_analytics_path else 'N/A'}"
        )
        print(
            f"Analytics Report File : {Path(document.financial_analytics_report_path).name if document.financial_analytics_report_path else 'N/A'}"
        )

        print("\nFinancial Analytics completed successfully.")
        print("=" * 70)

        return document
