from pathlib import Path
import json

from config import OUTPUT_DIR
from services.bank_statement_normalizer_service import (
    BankStatementNormalizerService,
)


class BankStatementNormalizerAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("BANK STATEMENT NORMALIZER")
        print("=" * 70)

        ####################################################
        # Normalize
        ####################################################

        dataframe = BankStatementNormalizerService.normalize(document.dataframe)

        document.dataframe = dataframe

        ####################################################
        # Output Folder
        ####################################################

        output_folder = (
            OUTPUT_DIR / Path(document.filename).stem / "normalized_dataframe"
        )

        output_folder.mkdir(parents=True, exist_ok=True)

        ####################################################
        # Save CSV
        ####################################################

        csv_file = output_folder / "normalized_dataframe.csv"

        dataframe.to_csv(
            csv_file,
            index=False,
            encoding="utf-8",
        )

        ####################################################
        # Save Info
        ####################################################

        info = {
            "rows": int(len(dataframe)),
            "columns": int(len(dataframe.columns)),
            "column_names": list(dataframe.columns),
        }

        info_file = output_folder / "normalization_info.json"

        with open(info_file, "w", encoding="utf-8") as file:
            json.dump(info, file, indent=4)

        ####################################################
        # Summary
        ####################################################

        print()
        print("Normalization Summary")
        print("----------------------------------------")
        print(f"Rows          : {len(dataframe)}")
        print(f"Columns       : {len(dataframe.columns)}")
        print(f"Folder        : {output_folder}")
        print(f"CSV           : {csv_file.name}")
        print(f"Info          : {info_file.name}")
        print()
        print("Bank Statement Normalization Completed.")
        print("=" * 70)

        return document
