from pathlib import Path

from config import OUTPUT_DIR
from services.bank_statement_excel_formatter_service import (
    BankStatementExcelFormatterService,
)


class BankStatementExcelFormatterAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("BANK STATEMENT EXCEL FORMATTER")
        print("=" * 70)

        ###########################################################
        # Data availability
        ###########################################################

        if document.dataframe is None or document.dataframe.empty:

            raise ValueError("No normalized dataframe available.")

        ###########################################################
        # Output folder
        ###########################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "excel"

        output_folder.mkdir(parents=True, exist_ok=True)

        excel_file = output_folder / "bank_statement.xlsx"

        ###########################################################
        # Create Excel
        ###########################################################

        BankStatementExcelFormatterService.export(
            dataframe=document.dataframe,
            output_path=excel_file,
        )

        ###########################################################
        # Update document
        ###########################################################

        document.excel_path = str(excel_file)

        ###########################################################
        # Summary
        ###########################################################

        print()
        print("Excel Formatter Summary")
        print("-" * 40)
        print(f"Rows          : {len(document.dataframe)}")
        print(f"Columns       : {len(document.dataframe.columns)}")
        print(f"Folder        : {output_folder}")
        print(f"Excel         : {excel_file.name}")

        print()
        print("Bank Statement Excel Formatter Completed.")
        print("=" * 70)

        return document
