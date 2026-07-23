from pathlib import Path
import json

from config import OUTPUT_DIR
from services.balance_sheet_response_builder import BalanceSheetResponseBuilder


class BalanceSheetResponseAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("BALANCE SHEET RESPONSE BUILDER")
        print("=" * 70)

        ############################################################
        # Build Response
        ############################################################

        document = BalanceSheetResponseBuilder.build(document)

        ############################################################
        # Output Folder
        ############################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        response_folder = output_folder / "response"

        response_folder.mkdir(parents=True, exist_ok=True)

        ############################################################
        # Save JSON Response
        ############################################################

        response_file = response_folder / "api_response.json"

        with open(
            response_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                document.response,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.response_path = str(response_file)

        ############################################################
        # Terminal Summary
        ############################################################

        response = document.response

        print("\nResponse Summary")
        print("-" * 40)

        print(f"Status         : {response.get('status')}")
        print(f"Document Type  : {response.get('document_type')}")

        metadata = response.get("metadata", {})

        print("\nMetadata")
        print("-" * 40)

        print(f"Rows           : {metadata.get('rows')}")
        print(f"Accounts       : {metadata.get('accounts')}")
        print(f"Sections       : {metadata.get('sections')}")
        print(f"Currency       : {metadata.get('currency')}")

        print("\nSummary")
        print("-" * 40)

        for key, value in response.get("summary", {}).items():
            print(f"{key:<30}: {value}")

        print("\nTable")
        print("-" * 40)

        print(f"Rows Returned  : {len(response.get('table', []))}")

        print("\nDownloads")
        print("-" * 40)

        downloads = response.get("downloads", {})

        print(f"CSV            : {downloads.get('csv')}")
        print(f"Excel          : {downloads.get('excel')}")

        print("\nSaved Response")
        print("-" * 40)

        print(response_file)

        print("\nBalance Sheet Response completed successfully.")
        print("=" * 70)

        return document
