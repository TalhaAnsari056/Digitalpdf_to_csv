from pathlib import Path
import json

from config import OUTPUT_DIR
from services.bank_statement_validator_service import (
    BankStatementValidatorService,
)


class BankStatementValidatorAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("BANK STATEMENT VALIDATION")
        print("=" * 70)

        ####################################################
        # Validate
        ####################################################

        report = BankStatementValidatorService.validate(document.normalized_dataframe)

        ####################################################
        # Output Folder
        ####################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "validation"

        output_folder.mkdir(parents=True, exist_ok=True)

        ####################################################
        # Save JSON Report
        ####################################################

        report_file = output_folder / "validation_report.json"

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        ####################################################
        # Save Human Readable Summary
        ####################################################

        summary_file = output_folder / "validation_summary.txt"

        with open(summary_file, "w", encoding="utf-8") as file:

            file.write("BANK STATEMENT VALIDATION\n")
            file.write("=" * 40 + "\n\n")

            file.write(f"Valid      : {report['valid']}\n")
            file.write(f"Errors     : {len(report['errors'])}\n")
            file.write(f"Warnings   : {len(report['warnings'])}\n\n")

            file.write("Statistics\n")
            file.write("-" * 20 + "\n")

            for key, value in report["statistics"].items():
                file.write(f"{key}: {value}\n")

            file.write("\n")

            if report["errors"]:
                file.write("Errors\n")
                file.write("-" * 20 + "\n")

                for error in report["errors"]:
                    file.write(f"- {error}\n")

                file.write("\n")

            if report["warnings"]:
                file.write("Warnings\n")
                file.write("-" * 20 + "\n")

                for warning in report["warnings"]:
                    file.write(f"- {warning}\n")

        ####################################################
        # Update Document
        ####################################################

        document.validation_report = report
        document.validation_report_path = str(report_file)

        ####################################################
        # Terminal Summary
        ####################################################

        stats = report["statistics"]

        print()
        print(f"Rows            : {stats['rows']}")
        print(f"Transactions    : {stats['transactions']}")
        print(f"Opening Balance : {stats['opening_balance']}")
        print(f"Closing Balance : {stats['closing_balance']}")
        print()

        print(f"Errors      : {len(report['errors'])}")
        print(f"Warnings    : {len(report['warnings'])}")
        print()

        if report["valid"]:
            print("Validation PASSED")
        else:
            print("Validation FAILED")

        print()
        print(f"Saved : {report_file}")
        print(f"Saved : {summary_file}")
        print("=" * 70)

        return document
