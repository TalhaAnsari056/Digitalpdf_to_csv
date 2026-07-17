from pathlib import Path
import json

from config import OUTPUT_DIR
from services.markdown_table_parser_service import MarkdownTableParserService


class MarkdownTableParserAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 60)
        print("MARKDOWN TABLE PARSER")
        print("=" * 60)

        ###########################################################
        # Parse markdown into DataFrame
        ###########################################################

        dataframe = MarkdownTableParserService.parse(document.markdown)

        document.dataframe = dataframe

        ###########################################################
        # Output folders
        ###########################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        dataframe_folder = output_folder / "dataframe"

        dataframe_folder.mkdir(parents=True, exist_ok=True)

        ###########################################################
        # Save parsed dataframe
        ###########################################################

        dataframe_file = dataframe_folder / "parsed_dataframe.csv"

        dataframe.to_csv(
            dataframe_file,
            index=False,
            encoding="utf-8",
        )

        ###########################################################
        # Save dataframe information
        ###########################################################

        info = {
            "rows": int(dataframe.shape[0]),
            "columns": int(dataframe.shape[1]),
            "column_names": list(dataframe.columns),
        }

        info_file = dataframe_folder / "dataframe_info.json"

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

        print(f"Rows    : {dataframe.shape[0]}")
        print(f"Columns : {dataframe.shape[1]}")
        print(f"Saved   : {dataframe_file}")

        return document
