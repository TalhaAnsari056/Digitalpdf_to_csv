from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from config import OUTPUT_DIR
from services.llm_service import LLMService


class LLMValidationService:
    """
    Validate LLM extracted markdown against the Marker cleaned markdown.

    Workflow

    Marker Markdown
            │
            ▼
      Parse into DataFrame

    LLM Markdown
            │
            ▼
      Parse into DataFrame

            │
            ▼
      Compare Rows

            │
      Missing Rows?
        /       \
      Yes       No
       │         │
       ▼         ▼
    Repair     Finish
       │
       ▼
    Repeat until complete
    """

    MAX_REPAIR_ATTEMPTS = 3

    ACCOUNT_COLUMN = "account_name"
    AMOUNT_COLUMN = "amount"

    SIMILARITY_THRESHOLD = 0.80

    ####################################################################
    # PUBLIC ENTRY
    ####################################################################

    @classmethod
    def validate(cls, document):

        print("\n" + "=" * 70)
        print("LLM VALIDATION")
        print("=" * 70)

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "llm" / "validation"

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = cls._validation_loop(
            document=document,
            output_folder=output_folder,
        )

        print()
        print("LLM Validation Completed.")
        print("=" * 70)

        ############################################################
        # Parse both markdowns
        ############################################################

        marker_dataframe = cls.parse_markdown(document.cleaned_markdown)

        llm_dataframe = cls.parse_markdown(document.llm_response)

        ############################################################
        # Save parsed dataframes
        ############################################################

        cls._save_dataframe(
            marker_dataframe,
            output_folder / "marker_dataframe.csv",
        )

        cls._save_dataframe(
            llm_dataframe,
            output_folder / "llm_dataframe.csv",
        )

        ############################################################
        # Find Missing Rows
        ############################################################

        missing_rows = cls._find_missing_rows(
            marker_dataframe,
            llm_dataframe,
        )

        ############################################################
        # Save Missing Rows
        ############################################################

        cls._save_json(
            missing_rows,
            output_folder / "missing_rows.json",
        )

        ############################################################
        # Terminal
        ############################################################

        print()

        print("=" * 70)
        print("VALIDATION RESULT")
        print("=" * 70)

        print(f"Marker Rows : {len(marker_dataframe)}")
        print(f"LLM Rows    : {len(llm_dataframe)}")
        print(f"Missing     : {len(missing_rows)}")

        print()

        if missing_rows:

            print("Missing Rows\n")

            for index, row in enumerate(missing_rows, start=1):

                print(f"{index:02d}. " f"{row['account_name']}    " f"{row['amount']}")

        else:

            print("No missing rows detected.")

        print()
        ############################################################
        # Continue later
        ############################################################

        # return {
        #     "document": document,
        #     "output_folder": output_folder,
        #     "marker_dataframe": marker_dataframe,
        #     "llm_dataframe": llm_dataframe,
        #     "missing_rows": missing_rows,
        # }

        document.validation_report = {
            "marker_rows": len(marker_dataframe),
            "llm_rows": len(llm_dataframe),
            "missing_rows": missing_rows,
        }

        report = {
            "marker_rows": len(marker_dataframe),
            "llm_rows": len(llm_dataframe),
            "missing_rows_count": len(missing_rows),
            "missing_rows": missing_rows,
        }

        report_file = output_folder / "validation_report.json"

        cls._save_json(
            report,
            report_file,
        )

        document.validation_report = report
        document.validation_report_path = str(report_file)

        return document

    ####################################################################
    # MARKDOWN PARSER
    ####################################################################

    @staticmethod
    def parse_markdown(markdown: str) -> pd.DataFrame:
        """
        Universal markdown parser.

        Supports BOTH

        1) Marker markdown
        2) LLM standardized markdown

        Returns

            account_name | amount
        """

        columns = ["account_name", "amount"]

        if markdown is None:
            return pd.DataFrame(columns=columns)

        markdown = markdown.strip()

        if markdown == "":
            return pd.DataFrame(columns=columns)

        ############################################################
        # Collect markdown rows only
        ############################################################

        table_lines = []

        for line in markdown.splitlines():

            line = line.strip()

            if not line.startswith("|"):
                continue

            # separator row
            stripped = line.replace("|", "").replace("-", "").replace(":", "").strip()

            if stripped == "":
                continue

            table_lines.append(line)

        if len(table_lines) < 2:
            return pd.DataFrame(columns=columns)

        ############################################################
        # Header
        ############################################################

        headers = [
            cell.strip().lower().replace(" ", "_")
            for cell in table_lines[0].strip("|").split("|")
        ]

        ############################################################
        # LLM STANDARD TABLE
        ############################################################

        if headers == ["account_name", "amount"]:

            records = []

            for line in table_lines[1:]:

                cells = [c.strip() for c in line.strip("|").split("|")]

                while len(cells) < 2:
                    cells.append("")

                records.append(
                    {
                        "account_name": cells[0],
                        "amount": cells[1],
                    }
                )

            dataframe = pd.DataFrame(records)

            dataframe = dataframe.fillna("").astype(str)

            return dataframe

        ############################################################
        # MARKER TABLE
        ############################################################

        records = []

        for line in table_lines[1:]:

            cells = [c.strip() for c in line.strip("|").split("|")]

            if len(cells) == 0:
                continue

            ########################################################
            # Left-most cell = account name
            ########################################################

            account_cell = cells[0].replace("<br>", "\n")

            ########################################################
            # Right-most non-empty cell = amount
            ########################################################

            amount_cell = ""

            for value in reversed(cells[1:]):

                value = value.strip()

                if value != "":
                    amount_cell = value
                    break

            ########################################################
            # Handle multi-line rows
            ########################################################

            account_lines = [x.strip() for x in account_cell.split("\n") if x.strip()]

            amount_lines = [
                x.strip()
                for x in amount_cell.replace("<br>", "\n").split("\n")
                if x.strip()
            ]

            ########################################################
            # One account
            ########################################################

            if len(account_lines) == 1:

                records.append(
                    {
                        "account_name": account_lines[0],
                        "amount": amount_lines[0] if amount_lines else "",
                    }
                )

                continue

            ########################################################
            # Multiple accounts
            ########################################################

            max_rows = max(
                len(account_lines),
                len(amount_lines),
            )

            for i in range(max_rows):

                records.append(
                    {
                        "account_name": (
                            account_lines[i] if i < len(account_lines) else ""
                        ),
                        "amount": amount_lines[i] if i < len(amount_lines) else "",
                    }
                )

        ############################################################
        # Final dataframe
        ############################################################

        dataframe = pd.DataFrame(records)

        dataframe = dataframe.fillna("").astype(str)

        ############################################################
        # Remove completely empty rows
        ############################################################

        dataframe = dataframe[
            (dataframe["account_name"].str.strip() != "")
            | (dataframe["amount"].str.strip() != "")
        ]

        dataframe = dataframe.reset_index(drop=True)

        return dataframe

    ####################################################################
    # FIND MISSING ROWS
    ####################################################################

    @classmethod
    def _find_missing_rows(
        cls,
        marker_df: pd.DataFrame,
        llm_df: pd.DataFrame,
    ):
        """
        Compare Marker rows against LLM rows.

        A row is considered matched when

        • amount is identical

        AND

        • account name similarity >= threshold.

        Returns
        -------
        list[dict]
        """

        missing_rows = []

        if marker_df.empty:
            return missing_rows

        if llm_df.empty:

            for index, row in marker_df.iterrows():

                missing_rows.append(
                    {
                        "marker_index": index,
                        "account_name": row["account_name"],
                        "amount": row["amount"],
                    }
                )

            return missing_rows

        ##############################################################

        from difflib import SequenceMatcher

        ##############################################################

        for marker_index, marker_row in marker_df.iterrows():

            marker_name = str(marker_row["account_name"]).strip().lower()

            marker_amount = str(marker_row["amount"]).strip()

            found = False

            ##########################################################

            for _, llm_row in llm_df.iterrows():

                llm_name = str(llm_row["account_name"]).strip().lower()

                llm_amount = str(llm_row["amount"]).strip()

                ######################################################
                # Amount must match first
                ######################################################

                if marker_amount != llm_amount:
                    continue

                ######################################################
                # Name similarity
                ######################################################

                similarity = SequenceMatcher(
                    None,
                    marker_name,
                    llm_name,
                ).ratio()

                if similarity >= cls.SIMILARITY_THRESHOLD:

                    found = True
                    break

            ##########################################################

            if not found:

                missing_rows.append(
                    {
                        "marker_index": marker_index,
                        "account_name": marker_row["account_name"],
                        "amount": marker_row["amount"],
                    }
                )

        return missing_rows

    ####################################################################
    # BUILD REPAIR PROMPT
    ####################################################################

    @staticmethod
    def _build_repair_prompt(
        marker_markdown: str,
        llm_markdown: str,
        missing_rows: list,
    ):

        missing_table = "\n".join(
            f"| {row['account_name']} | {row['amount']} |" for row in missing_rows
        )

        return f"""
    You are correcting a Balance Sheet extraction.

    The CURRENT markdown generated by the LLM is missing some rows.

    Your task is ONLY to insert the missing rows into the correct position.

    DO NOT change existing rows.

    DO NOT remove rows.

    DO NOT modify values.

    DO NOT reorder rows.

    DO NOT rename accounts.

    Insert ONLY the missing rows.

    Return ONLY the complete corrected markdown table.

    ==========================================================
    ORIGINAL MARKER MARKDOWN
    ==========================================================

    {marker_markdown}

    ==========================================================
    CURRENT LLM MARKDOWN
    ==========================================================

    {llm_markdown}

    ==========================================================
    MISSING ROWS
    ==========================================================

    | account_name | amount |
    |--------------|--------|
    {missing_table}
    """

    ####################################################################
    # REPAIR USING LLM
    ####################################################################

    @classmethod
    def _repair_with_llm(
        cls,
        marker_markdown: str,
        llm_markdown: str,
        missing_rows: list,
        output_folder: Path,
        attempt: int,
    ):

        ############################################################
        # Build Prompt
        ############################################################

        prompt = cls._build_repair_prompt(
            marker_markdown,
            llm_markdown,
            missing_rows,
        )

        ############################################################
        # Attempt Folder
        ############################################################

        attempt_folder = output_folder / f"attempt_{attempt}"

        attempt_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        ############################################################
        # Save Prompt
        ############################################################

        cls._save_text(
            prompt,
            attempt_folder / "repair_prompt.txt",
        )

        ############################################################
        # Call LLM
        ############################################################

        repaired_markdown = LLMService.generate(prompt)

        ############################################################
        # Save Response
        ############################################################

        cls._save_text(
            repaired_markdown,
            attempt_folder / "repaired_markdown.md",
        )

        return repaired_markdown

    ####################################################################
    # VALIDATION LOOP
    ####################################################################

    @classmethod
    def _validation_loop(
        cls,
        document,
        output_folder: Path,
    ):

        marker_markdown = document.cleaned_markdown

        current_markdown = document.mapped_markdown

        final_missing_rows = []

        total_attempts = 0

        ############################################################
        # Parse Marker Once
        ############################################################

        marker_df = cls.parse_markdown(marker_markdown)

        cls._save_dataframe(
            marker_df,
            output_folder / "marker_dataframe.csv",
        )

        ############################################################
        # Iterative Repair
        ############################################################

        for attempt in range(1, cls.MAX_REPAIR_ATTEMPTS + 1):

            print()
            print(f"Validation Attempt {attempt}")
            print("-" * 40)

            total_attempts = attempt

            ########################################################
            # Parse Current LLM Output
            ########################################################

            llm_df = cls.parse_markdown(current_markdown)

            cls._save_dataframe(
                llm_df,
                output_folder / "llm_dataframe.csv",
            )

            ########################################################
            # Find Missing Rows
            ########################################################

            missing_rows = cls._find_missing_rows(
                marker_df,
                llm_df,
            )

            final_missing_rows = missing_rows

            ########################################################
            # Save Missing Rows
            ########################################################

            attempt_folder = output_folder / f"attempt_{attempt}"

            attempt_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            cls._save_json(
                missing_rows,
                attempt_folder / "missing_rows.json",
            )

            ########################################################
            # Terminal
            ########################################################

            print(f"Missing Rows : {len(missing_rows)}")

            ########################################################
            # Validation Passed
            ########################################################

            if len(missing_rows) == 0:

                print("Validation Passed.")

                break

            ########################################################
            # Repair
            ########################################################

            print("Repairing with LLM...")

            current_markdown = cls._repair_with_llm(
                marker_markdown=marker_markdown,
                llm_markdown=current_markdown,
                missing_rows=missing_rows,
                output_folder=output_folder,
                attempt=attempt,
            )

        ############################################################
        # Save Final Markdown
        ############################################################

        # cls._save_text(
        #     current_markdown,
        #     output_folder / "validated_markdown.md",
        # )
        validated_markdown_file = output_folder / "validated_markdown.md"

        cls._save_text(
            current_markdown,
            validated_markdown_file,
        )

        ############################################################
        # Update Document
        ############################################################

        document.validated_markdown = current_markdown
        document.validated_markdown_path = str(validated_markdown_file)
        ############################################################
        # Validation Report
        ############################################################

        report = {
            "attempts": total_attempts,
            "missing_rows": len(final_missing_rows),
            "passed": len(final_missing_rows) == 0,
        }

        cls._save_validation_report(
            report,
            output_folder,
        )

        ############################################################
        # Update Document
        ############################################################

        # document.validated_markdown = current_markdown

        document.validation_report = report

        return document

    ####################################################################
    # SAVE DATAFRAME
    ####################################################################
    @staticmethod
    def _save_dataframe(dataframe: pd.DataFrame, file_path: Path):

        dataframe.to_csv(
            file_path,
            index=False,
            encoding="utf-8-sig",
        )

    ####################################################################
    # SAVE JSON
    ####################################################################

    @staticmethod
    def _save_json(data: dict | list, file_path: Path):

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    ####################################################################
    # SAVE TEXT
    ####################################################################

    @staticmethod
    def _save_text(text: str, file_path: Path):

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(text)

    ####################################################################
    # SAVE VALIDATION REPORT
    ####################################################################

    @staticmethod
    def _save_validation_report(
        report: dict,
        output_folder: Path,
    ):

        with open(
            output_folder / "validation_report.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )
