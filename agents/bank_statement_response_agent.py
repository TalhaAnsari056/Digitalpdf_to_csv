from pathlib import Path
import json

from config import OUTPUT_DIR
from services.bank_statement_response_builder_service import (
    BankStatementResponseBuilderService,
)


class BankStatementResponseAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("BANK STATEMENT RESPONSE BUILDER")
        print("=" * 70)

        ############################################################
        # Build Response
        ############################################################

        response = BankStatementResponseBuilderService.build(document)

        ############################################################
        # Output Folder
        ############################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "response"

        output_folder.mkdir(parents=True, exist_ok=True)

        ############################################################
        # Save Response JSON
        ############################################################

        response_file = output_folder / "response.json"

        with open(
            response_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                response,
                file,
                indent=4,
                ensure_ascii=False,
            )

        ############################################################
        # Update Document
        ############################################################

        document.response = response
        document.response_path = str(response_file)

        ############################################################
        # Terminal Debug
        ############################################################

        print("\nResponse Summary")
        print("-" * 40)
        print(f"Status           : {response['status']}")
        print(f"Document Type    : {response['document_type']}")
        print(f"Rows             : {response['metadata']['rows']}")
        print(f"Currency         : {response['metadata']['currency'] or 'N/A'}")
        print(f"Transactions     : {response['summary']['transaction_count']}")
        print(f"Opening Balance  : {response['summary']['opening_balance']}")
        print(f"Closing Balance  : {response['summary']['closing_balance']}")
        print(f"Total Debit      : {response['summary']['total_debit']}")
        print(f"Total Credit     : {response['summary']['total_credit']}")
        print(f"Table Rows       : {len(response['table'])}")
        print(f"Response JSON    : {response_file}")

        print("\nResponse Builder completed successfully.")
        print("=" * 70)

        return document
