from __future__ import annotations

import pandas as pd


class MarkdownTableParserService:

    # REQUIRED_COLUMNS = [
    #     "row_type",
    #     "section",
    #     "subsection",
    #     "account_code",
    #     "account_name",
    #     "amount",
    #     "currency",
    # ]
    BALANCE_SHEET_COLUMNS = [
        "row_type",
        "section",
        "subsection",
        "account_code",
        "account_name",
        "amount",
        "currency",
    ]

    BANK_STATEMENT_COLUMNS = [
        "row_type",
        "date",
        "description",
        "debit",
        "credit",
        "balance",
        "currency",
    ]

    @staticmethod
    def _is_separator(line: str) -> bool:
        """
        Detect markdown separator row.

        Example:
        |-----|------|-----|
        """

        text = line.replace("|", "").replace("-", "").replace(":", "").strip()

        return text == ""

    @classmethod
    def parse(cls, markdown: str, document_type: str) -> pd.DataFrame:

        if markdown is None:
            raise ValueError("Markdown is None.")

        markdown = markdown.strip()

        if markdown == "":
            raise ValueError("Empty markdown received.")

        ##############################################################
        # Keep only markdown table rows
        ##############################################################

        table_lines = []

        for line in markdown.splitlines():

            line = line.strip()

            if not line.startswith("|"):
                continue

            if cls._is_separator(line):
                continue

            table_lines.append(line)

        if len(table_lines) < 2:
            raise ValueError("No markdown table found.")

        ##############################################################
        # Header
        ##############################################################

        headers = [
            cell.strip().lower().replace(" ", "_")
            for cell in table_lines[0].strip("|").split("|")
        ]
        print("\nDetected Headers")
        print(headers)

        ##############################################################
        # Validate expected columns
        ##############################################################
        print("\nDetected Headers")
        print(headers)
        # missing = []

        # for column in cls.REQUIRED_COLUMNS:

        #     if column not in headers:
        #         missing.append(column)
        if document_type == "balance_sheet":

            required_columns = cls.BALANCE_SHEET_COLUMNS

        elif document_type == "bank_statement":

            required_columns = cls.BANK_STATEMENT_COLUMNS

        else:

            raise ValueError(f"Unsupported document type: {document_type}")

        missing = []

        for column in required_columns:

            if column not in headers:
                missing.append(column)

        if missing:
            raise ValueError(f"Missing required markdown columns: {missing}")

        ##############################################################
        # Parse rows
        ##############################################################

        records = []

        for line in table_lines[1:]:

            cells = [cell.strip() for cell in line.strip("|").split("|")]

            # Fix short rows

            if len(cells) < len(headers):

                cells.extend([""] * (len(headers) - len(cells)))

            # Ignore extra cells instead of crashing

            if len(cells) > len(headers):

                cells = cells[: len(headers)]

            record = dict(zip(headers, cells))

            records.append(record)

        ##############################################################
        # DataFrame
        ##############################################################

        dataframe = pd.DataFrame(records)

        dataframe = dataframe.fillna("")

        dataframe = dataframe.astype(str)

        ##############################################################
        # Terminal Debug
        ##############################################################

        print("\n" + "=" * 60)
        print("PARSED DATAFRAME")
        print("=" * 60)

        print(f"Rows    : {len(dataframe)}")
        print(f"Columns : {len(dataframe.columns)}")

        print()

        print(dataframe.head(10))

        print("=" * 60)
        print()

        return dataframe
