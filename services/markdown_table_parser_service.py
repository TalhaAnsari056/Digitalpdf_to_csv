import json
from pathlib import Path

from config import OUTPUT_DIR


class MarkdownTableParserService:

    @staticmethod
    def parse(document):

        print("\n" + "=" * 60)
        print("MARKDOWN TABLE PARSER")
        print("=" * 60)

        markdown = document.llm_response.strip()

        lines = []

        for line in markdown.splitlines():

            line = line.strip()

            if line.startswith("|"):

                lines.append(line)

        if len(lines) < 2:
            raise Exception("No markdown table found.")

        # -----------------------------------------
        # Header
        # -----------------------------------------

        headers = [column.strip() for column in lines[0].strip("|").split("|")]

        # -----------------------------------------
        # Skip separator row
        # -----------------------------------------

        data_lines = lines[2:]

        records = []

        for line in data_lines:

            values = [value.strip() for value in line.strip("|").split("|")]

            # pad missing columns
            while len(values) < len(headers):
                values.append("")

            # remove extra columns
            values = values[: len(headers)]

            records.append(dict(zip(headers, values)))

        document.parsed_rows = records

        # -----------------------------------------
        # Save JSON (debugging only)
        # -----------------------------------------

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        parsed_folder = output_folder / "parsed"

        parsed_folder.mkdir(parents=True, exist_ok=True)

        parsed_file = parsed_folder / "parsed_rows.json"

        with open(
            parsed_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                records,
                file,
                indent=4,
                ensure_ascii=False,
            )

        print(f"Rows Parsed : {len(records)}")
        print(f"Saved       : {parsed_file}")

        return document
