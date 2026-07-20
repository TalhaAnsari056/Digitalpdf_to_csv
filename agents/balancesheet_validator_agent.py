from pathlib import Path
import json

from config import OUTPUT_DIR
from services.balancesheet_validator_service import (
    BalanceSheetValidatorService,
)


class BalanceSheetValidatorAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("BALANCE SHEET VALIDATION")
        print("=" * 70)

        ###########################################################
        # Validate
        ###########################################################

        report = BalanceSheetValidatorService.validate(document.dataframe)

        document.validation_report = report

        ###########################################################
        # Output folder
        ###########################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        validation_folder = output_folder / "validation"

        validation_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        ###########################################################
        # Save JSON
        ###########################################################

        json_file = validation_folder / "validation_report.json"

        with open(
            json_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        ###########################################################
        # Save Summary
        ###########################################################

        summary_file = validation_folder / "validation_summary.txt"

        with open(
            summary_file,
            "w",
            encoding="utf-8",
        ) as file:

            file.write("Balance Sheet Validation Summary\n")
            file.write("=" * 40 + "\n\n")

            for key, value in report["statistics"].items():

                file.write(f"{key}: {value}\n")

            file.write("\n")

            file.write(f"Errors   : {len(report['errors'])}\n")
            file.write(f"Warnings : {len(report['warnings'])}\n")
            file.write(f"Valid    : {report['valid']}\n")

        ###########################################################
        # Terminal
        ###########################################################

        print()

        for key, value in report["statistics"].items():

            print(f"{key.capitalize():<15}: {value}")

        print()

        print(f"Errors      : {len(report['errors'])}")
        print(f"Warnings    : {len(report['warnings'])}")

        if report["valid"]:

            print("\nValidation PASSED")

        else:

            print("\nValidation FAILED")

        print(f"\nSaved : {json_file}")
        print(f"Saved : {summary_file}")

        print("=" * 70)

        return document
