from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class BankStatementResponseBuilderService:

    @classmethod
    def build(cls, document) -> dict:

        dataframe = document.dataframe

        return {
            "status": "success",
            "document_type": document.document_type,
            "metadata": cls._build_metadata(document),
            "summary": cls._build_summary(dataframe),
            "table": cls._build_table(dataframe),
            "downloads": cls._build_downloads(document),
        }

    ####################################################################
    # Metadata
    ####################################################################

    @staticmethod
    def _build_metadata(document) -> dict:

        dataframe = document.dataframe

        currency = ""

        if (
            dataframe is not None
            and not dataframe.empty
            and "currency" in dataframe.columns
        ):

            values = dataframe["currency"].fillna("").astype(str).str.strip()

            values = values[values != ""]

            if not values.empty:
                currency = values.iloc[0]

        return {
            "filename": Path(document.filename).name,
            "document_type": document.document_type,
            "rows": 0 if dataframe is None else int(len(dataframe)),
            "currency": currency,
        }

    ####################################################################
    # Safe Numeric Conversion
    ####################################################################

    @staticmethod
    def _to_number(series: pd.Series) -> pd.Series:
        """
        Safely convert numeric-looking values.

        Handles:

        12,500
        PKR 12,500
        USD 100
        $250
        €100
        £500
        None
        N/A
        -
        empty strings

        Invalid values become 0.
        """

        if series is None:
            return pd.Series(dtype=float)

        cleaned = (
            series.fillna("")
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("PKR", "", regex=False)
            .str.replace("USD", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace("€", "", regex=False)
            .str.replace("£", "", regex=False)
            .str.strip()
        )

        return pd.to_numeric(
            cleaned,
            errors="coerce",
        ).fillna(0)

    ####################################################################
    # Summary
    ####################################################################

    @classmethod
    def _build_summary(cls, dataframe: pd.DataFrame) -> dict:

        if dataframe is None or dataframe.empty:

            return {
                "opening_balance": None,
                "closing_balance": None,
                "transaction_count": 0,
                "total_debit": 0,
                "total_credit": 0,
            }

        df = dataframe.copy()

        ############################################################
        # Ensure required columns exist
        ############################################################

        for column in (
            "row_type",
            "debit",
            "credit",
            "balance",
        ):

            if column not in df.columns:
                df[column] = ""

        ############################################################
        # Numeric conversion
        ############################################################

        df["debit"] = cls._to_number(df["debit"])
        df["credit"] = cls._to_number(df["credit"])
        df["balance"] = cls._to_number(df["balance"])

        ############################################################
        # Opening Balance
        ############################################################

        opening = None

        opening_rows = df[df["row_type"].astype(str).str.upper() == "OPENING_BALANCE"]

        if not opening_rows.empty:

            opening = float(opening_rows.iloc[0]["balance"])

        ############################################################
        # Closing Balance
        #
        # IMPORTANT:
        # Do NOT infer closing balance.
        # Only return it if the document explicitly contains one.
        ############################################################

        closing = None

        closing_rows = df[df["row_type"].astype(str).str.upper() == "CLOSING_BALANCE"]

        if not closing_rows.empty:

            closing = float(closing_rows.iloc[-1]["balance"])

        ############################################################
        # Transactions
        ############################################################

        transactions = df[df["row_type"].astype(str).str.upper() == "TRANSACTION"]

        return {
            "opening_balance": opening,
            "closing_balance": closing,
            "transaction_count": int(len(transactions)),
            "total_debit": round(float(transactions["debit"].sum()), 2),
            "total_credit": round(float(transactions["credit"].sum()), 2),
        }

    ####################################################################
    # Table
    ####################################################################

    @staticmethod
    def _build_table(dataframe: pd.DataFrame) -> list[dict[str, Any]]:

        if dataframe is None or dataframe.empty:
            return []

        return dataframe.fillna("").to_dict(orient="records")

    ####################################################################
    # Downloads
    ####################################################################

    @staticmethod
    def _build_downloads(document) -> dict:

        return {
            "csv": document.csv_path,
            "excel": document.excel_path,
        }
