import re
import pandas as pd


class BankStatementNormalizerService:

    @classmethod
    def normalize(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize a parsed bank statement dataframe.

        This stage never changes the meaning of the data.
        It only standardizes formatting.
        """

        dataframe = dataframe.copy()

        dataframe = cls._normalize_empty_values(dataframe)
        dataframe = cls._trim_strings(dataframe)
        dataframe = cls._normalize_row_type(dataframe)
        dataframe = cls._normalize_date(dataframe)
        dataframe = cls._normalize_amount_columns(dataframe)
        dataframe = cls._normalize_currency(dataframe)

        ####################################################
        # Remove exact duplicate rows
        ####################################################

        dataframe = dataframe.drop_duplicates(ignore_index=True)

        ####################################################
        # Debug
        ####################################################

        print("\n" + "=" * 70)
        print("BANK STATEMENT AFTER NORMALIZATION")
        print("=" * 70)

        columns_to_show = [
            column
            for column in [
                "row_type",
                "date",
                "description",
                "debit",
                "credit",
                "balance",
                "currency",
            ]
            if column in dataframe.columns
        ]

        print(dataframe[columns_to_show].to_string(index=False))

        print("=" * 70)
        print()

        return dataframe.reset_index(drop=True)

    # ==========================================================
    # EMPTY VALUES
    # ==========================================================

    @staticmethod
    def _normalize_empty_values(dataframe: pd.DataFrame) -> pd.DataFrame:

        return dataframe.fillna("")

    # ==========================================================
    # TRIM STRINGS
    # ==========================================================

    @staticmethod
    def _trim_strings(dataframe: pd.DataFrame) -> pd.DataFrame:

        for column in dataframe.columns:

            dataframe[column] = (
                dataframe[column]
                .astype(str)
                .str.replace("\u00a0", " ", regex=False)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
            )

        return dataframe

    # ==========================================================
    # ROW TYPE
    # ==========================================================

    @staticmethod
    def _normalize_row_type(dataframe: pd.DataFrame) -> pd.DataFrame:

        if "row_type" not in dataframe.columns:
            return dataframe

        dataframe["row_type"] = (
            dataframe["row_type"].astype(str).str.upper().str.strip()
        )

        return dataframe

    # ==========================================================
    # DATE
    # ==========================================================

    @staticmethod
    def _normalize_date(dataframe: pd.DataFrame) -> pd.DataFrame:

        if "date" not in dataframe.columns:
            return dataframe

        dataframe["date"] = (
            dataframe["date"]
            .astype(str)
            .str.replace("<br>", " ", regex=False)
            .str.replace("\n", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        return dataframe

    # ==========================================================
    # DEBIT / CREDIT / BALANCE
    # ==========================================================

    @classmethod
    def _normalize_amount_columns(cls, dataframe: pd.DataFrame) -> pd.DataFrame:

        for column in ["debit", "credit", "balance"]:

            if column not in dataframe.columns:
                continue

            dataframe[column] = dataframe[column].apply(cls._clean_amount)

        return dataframe

    @staticmethod
    def _clean_amount(value):

        if value is None:
            return ""

        value = str(value).strip()

        if value == "":
            return ""

        value = value.replace(",", "")

        ####################################################
        # (125.50) -> -125.50
        ####################################################

        if re.fullmatch(r"\(.*\)", value):

            value = "-" + value[1:-1].strip()

        ####################################################
        # Remove currency symbols
        ####################################################

        symbols = [
            "$",
            "€",
            "£",
            "Rs.",
            "Rs",
            "PKR",
            "USD",
            "AED",
        ]

        for symbol in symbols:
            value = value.replace(symbol, "")

        return value.strip()

    # ==========================================================
    # CURRENCY
    # ==========================================================

    @staticmethod
    def _normalize_currency(dataframe: pd.DataFrame) -> pd.DataFrame:

        if "currency" not in dataframe.columns:
            return dataframe

        dataframe["currency"] = (
            dataframe["currency"].astype(str).str.upper().str.strip()
        )

        return dataframe
