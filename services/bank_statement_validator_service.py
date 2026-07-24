from __future__ import annotations

import re
from datetime import datetime

import pandas as pd


class BankStatementValidatorService:

    REQUIRED_COLUMNS = [
        "row_type",
        "date",
        "description",
        "debit",
        "credit",
        "balance",
        "currency",
    ]

    VALID_ROW_TYPES = {
        "OPENING_BALANCE",
        "TRANSACTION",
        "CLOSING_BALANCE",
        "SUMMARY",
    }

    DATE_FORMATS = [
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%d/%m/%Y",
        "%d-%m-%y",
    ]

    # ==========================================================
    # PUBLIC
    # ==========================================================

    @classmethod
    def validate(cls, dataframe: pd.DataFrame) -> dict:

        errors = []
        warnings = []

        ########################################################
        # Required Columns
        ########################################################

        missing = [
            column for column in cls.REQUIRED_COLUMNS if column not in dataframe.columns
        ]

        if missing:

            errors.append(f"Missing required columns: {', '.join(missing)}")

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "statistics": {},
            }

        ########################################################
        # Statistics
        ########################################################

        row_types = dataframe["row_type"].astype(str).str.upper().str.strip()

        statistics = {
            "rows": int(len(dataframe)),
            "opening_balance": int((row_types == "OPENING_BALANCE").sum()),
            "transactions": int((row_types == "TRANSACTION").sum()),
            "closing_balance": int((row_types == "CLOSING_BALANCE").sum()),
            "summary": int((row_types == "SUMMARY").sum()),
        }

        ########################################################
        # Row Validation
        ########################################################

        for index, row in dataframe.iterrows():

            row_number = index + 2

            row_type = str(row["row_type"]).strip().upper()

            date = str(row["date"]).strip()

            description = str(row["description"]).strip()

            debit = str(row["debit"]).strip()

            credit = str(row["credit"]).strip()

            balance = str(row["balance"]).strip()

            currency = str(row["currency"]).strip()

            ####################################################
            # Row Type
            ####################################################

            if row_type not in cls.VALID_ROW_TYPES:

                warnings.append(f"Unknown row_type '{row_type}' at row {row_number}")

            ####################################################
            # Date
            ####################################################

            if date:

                if not cls._valid_date(date):

                    warnings.append(f"Invalid date '{date}' at row {row_number}")

            ####################################################
            # Numeric Fields
            ####################################################

            for field_name, value in [
                ("debit", debit),
                ("credit", credit),
                ("balance", balance),
            ]:

                if value != "" and not cls._is_number(value):

                    errors.append(f"Invalid {field_name} '{value}' at row {row_number}")

            ####################################################
            # Debit / Credit Rule
            ####################################################

            if row_type == "TRANSACTION":

                has_debit = debit != ""
                has_credit = credit != ""

                if has_debit and has_credit:

                    warnings.append(
                        f"Both debit and credit populated at row {row_number}"
                    )

                if not has_debit and not has_credit:

                    warnings.append(
                        f"Transaction without debit/credit at row {row_number}"
                    )

            ####################################################
            # Empty Description
            ####################################################

            if row_type == "TRANSACTION":

                if description == "":

                    warnings.append(f"Missing description at row {row_number}")

        ########################################################
        # Opening Balance
        ########################################################

        if statistics["opening_balance"] > 1:

            warnings.append("Multiple OPENING_BALANCE rows detected.")

        ########################################################
        # Closing Balance
        ########################################################

        if statistics["closing_balance"] > 1:

            warnings.append("Multiple CLOSING_BALANCE rows detected.")

        ########################################################
        # Currency
        ########################################################

        currencies = dataframe["currency"].astype(str).str.strip()

        currencies = {c for c in currencies if c != ""}

        if len(currencies) > 1:

            warnings.append("Multiple currencies detected.")

        ########################################################
        # Result
        ########################################################

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "statistics": statistics,
        }

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _is_number(value: str) -> bool:

        value = value.replace(",", "").strip()

        try:
            float(value)
            return True
        except Exception:
            return False

    @classmethod
    def _valid_date(cls, value: str) -> bool:

        value = value.strip()

        for fmt in cls.DATE_FORMATS:

            try:
                datetime.strptime(value, fmt)
                return True
            except Exception:
                pass

        return False
