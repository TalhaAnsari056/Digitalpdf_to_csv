import re
import pandas as pd


class BalanceSheetValidatorService:

    REQUIRED_COLUMNS = [
        "row_type",
        "section",
        "subsection",
        "account_code",
        "account_name",
        "amount",
        "currency",
    ]

    VALID_ROW_TYPES = {
        "SECTION",
        "SUBSECTION",
        "ACCOUNT",
        "TOTAL",
    }

    @classmethod
    def validate(cls, dataframe: pd.DataFrame) -> dict:

        report = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {},
        }

        ############################################################
        # Required columns
        ############################################################

        for column in cls.REQUIRED_COLUMNS:

            if column not in dataframe.columns:

                report["errors"].append(f"Missing required column: {column}")

        if report["errors"]:

            report["valid"] = False
            return report

        ############################################################
        # Statistics
        ############################################################

        report["statistics"] = {
            "rows": int(len(dataframe)),
            "sections": int((dataframe["row_type"] == "SECTION").sum()),
            "subsections": int((dataframe["row_type"] == "SUBSECTION").sum()),
            "accounts": int((dataframe["row_type"] == "ACCOUNT").sum()),
            "totals": int((dataframe["row_type"] == "TOTAL").sum()),
        }

        ############################################################
        # Row validation
        ############################################################

        for index, row in dataframe.iterrows():

            row_no = index + 1

            row_type = str(row["row_type"]).strip().upper()

            section = str(row["section"]).strip()

            subsection = str(row["subsection"]).strip()

            account_code = str(row["account_code"]).strip()

            account_name = str(row["account_name"]).strip()

            amount = str(row["amount"]).strip()

            ########################################################

            if row_type not in cls.VALID_ROW_TYPES:

                report["errors"].append(f"Row {row_no}: Invalid row_type '{row_type}'")

                continue

            ########################################################
            # SECTION
            ########################################################

            if row_type == "SECTION":

                if section == "":

                    report["errors"].append(
                        f"Row {row_no}: SECTION missing section name."
                    )

            ########################################################
            # SUBSECTION
            ########################################################

            elif row_type == "SUBSECTION":

                if subsection == "":

                    report["warnings"].append(
                        f"Row {row_no}: SUBSECTION has empty subsection."
                    )

            ########################################################
            # ACCOUNT
            ########################################################

            elif row_type == "ACCOUNT":

                if account_name == "":

                    report["errors"].append(
                        f"Row {row_no}: ACCOUNT missing account name."
                    )

                if section == "":

                    report["warnings"].append(f"Row {row_no}: ACCOUNT without section.")

            ########################################################
            # TOTAL
            ########################################################

            elif row_type == "TOTAL":

                if account_code != "":

                    report["warnings"].append(
                        f"Row {row_no}: TOTAL should not contain account code."
                    )

            ########################################################
            # Amount validation
            ########################################################

            if amount != "":

                if not re.fullmatch(r"-?\d+(\.\d+)?", amount):

                    report["warnings"].append(
                        f"Row {row_no}: Non-numeric amount '{amount}'"
                    )

        ############################################################
        # Duplicate account codes
        ############################################################

        account_rows = dataframe[dataframe["row_type"] == "ACCOUNT"]

        duplicates = account_rows[account_rows["account_code"] != ""][
            "account_code"
        ].duplicated()

        if duplicates.any():

            duplicate_codes = account_rows.loc[
                duplicates,
                "account_code",
            ].tolist()

            report["warnings"].append(
                f"Duplicate account codes: {', '.join(duplicate_codes)}"
            )

        ############################################################

        if report["errors"]:

            report["valid"] = False

        return report
