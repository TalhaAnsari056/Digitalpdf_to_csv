from pathlib import Path
import json

from config import OUTPUT_DIR
from services.balancesheet_normalizer_service import (
    BalancesheetNormalizerService,
)


class BalanceSheetNormalizerAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("BALANCE SHEET NORMALIZER")
        print("=" * 70)

        ###########################################################
        # Normalize dataframe
        ###########################################################

        dataframe = BalancesheetNormalizerService.normalize(document.dataframe)

        document.dataframe = dataframe

        ###########################################################
        # Output folders
        ###########################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        normalize_folder = output_folder / "normalized_dataframe"

        normalize_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        ###########################################################
        # Save normalized dataframe
        ###########################################################

        normalized_csv = normalize_folder / "normalized_dataframe.csv"

        dataframe.to_csv(
            normalized_csv,
            index=False,
            encoding="utf-8",
        )

        ###########################################################
        # Save metadata
        ###########################################################

        info = {
            "rows": int(dataframe.shape[0]),
            "columns": int(dataframe.shape[1]),
            "column_names": list(dataframe.columns),
            "column_types": {
                column: str(dtype) for column, dtype in dataframe.dtypes.items()
            },
        }

        info_file = normalize_folder / "normalization_info.json"

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

        ###########################################################
        # Terminal
        ###########################################################

        print("\nNormalization Summary")
        print("-" * 40)
        print(f"Rows          : {dataframe.shape[0]}")
        print(f"Columns       : {dataframe.shape[1]}")
        print(f"Folder        : {normalize_folder}")
        print(f"CSV           : {normalized_csv.name}")
        print(f"Info          : {info_file.name}")

        print("\nBalance Sheet Normalization Completed.")
        print("=" * 70)

        return document
