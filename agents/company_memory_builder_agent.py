from pathlib import Path

from services.company_memory_builder_service import CompanyMemoryBuilderService


class CompanyMemoryBuilderAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("COMPANY MEMORY BUILDER")
        print("=" * 70)

        ############################################################
        # Orchestration only
        ############################################################

        company_profiles = CompanyMemoryBuilderService.process()

        ############################################################
        # Terminal Summary
        ############################################################

        print("\nCompany Memory Summary")
        print("-" * 40)
        print(
            f"Company Memory File : {Path(document.company_memory_path).name if document.company_memory_path else 'N/A'}"
        )
        print(
            f"Report File          : {Path(document.company_memory_report_path).name if document.company_memory_report_path else 'N/A'}"
        )
        print(
            f"Companies Processed  : {len(company_profiles) if company_profiles is not None else 'N/A'}"
        )
        print(
            f"Documents Processed  : {len(company_profiles) if company_profiles is not None else 'N/A'}"
        )

        print("\nCompany Memory completed successfully.")
        print("=" * 70)

        return document
