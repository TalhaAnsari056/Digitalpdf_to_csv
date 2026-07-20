from pathlib import Path
import json

from config import OUTPUT_DIR
from services.excel_formatter_service import ExcelFormatterService


class ExcelFormatterAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("EXCEL FORMATTER")
        print("=" * 70)

        ############################################################
        # Validate dataframe
        ############################################################

        if document.dataframe is None:

            raise ValueError("No normalized dataframe available for Excel formatting.")

        ############################################################
        # Output folders
        ############################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        excel_folder = output_folder / "excel"

        excel_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        ############################################################
        # Excel file
        ############################################################

        excel_file = excel_folder / "formatted_balance_sheet.xlsx"

        ############################################################
        # Create workbook
        ############################################################

        ExcelFormatterService.export(
            dataframe=document.dataframe,
            output_file=excel_file,
        )

        ############################################################
        # Save document path
        ############################################################

        document.excel_path = str(excel_file)

        ############################################################
        # Debug information
        ############################################################

        info = {
            "rows": int(document.dataframe.shape[0]),
            "columns": int(document.dataframe.shape[1]),
            "worksheet": "Balance Sheet",
            "output_file": excel_file.name,
        }

        info_file = excel_folder / "excel_info.json"

        with open(
            info_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                info,
                file,
                indent=4,
                ensure_ascii=False,
            )

        ############################################################
        # Terminal
        ############################################################

        print("\nExcel Formatting Summary")
        print("-" * 40)

        print(f"Rows          : {document.dataframe.shape[0]}")
        print(f"Columns       : {document.dataframe.shape[1]}")
        print(f"Folder        : {excel_folder}")
        print(f"Workbook      : {excel_file.name}")
        print(f"Info          : {info_file.name}")

        print("\nExcel Formatter completed successfully.")
        print("=" * 70)

        return document
