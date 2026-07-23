from pathlib import Path
import json


class BalanceSheetResponseBuilder:

    @classmethod
    def build(cls, document):

        response = {
            "status": "success",
            "document_type": document.document_type,
            "metadata": cls._build_metadata(document),
            "summary": cls._build_summary(document),
            "table": cls._build_table(document),
            "downloads": cls._build_downloads(document),
        }

        print("\n" + "=" * 80)
        print("BALANCE SHEET RESPONSE")
        print("=" * 80)
        print(json.dumps(response, indent=4, ensure_ascii=False))
        print("=" * 80)
        print(response["metadata"])
        print("=" * 80)
        print(response["summary"])
        print("=" * 80)
        print(response["table"][:5])
        print("=" * 80)

        document.response = response
        return document

    # ==========================================================
    # METADATA
    # ==========================================================

    # ==========================================================
    # METADATA
    # ==========================================================

    @staticmethod
    def _build_metadata(document):

        dataframe = document.dataframe

        #########################################################
        # Row statistics
        #########################################################

        row_count = len(dataframe)

        sections = 0
        subsections = 0
        accounts = 0
        totals = 0

        if "row_type" in dataframe.columns:

            row_types = (
                dataframe["row_type"].fillna("").astype(str).str.upper().str.strip()
            )

            sections = int((row_types == "SECTION").sum())
            subsections = int((row_types == "SUBSECTION").sum())
            accounts = int((row_types == "ACCOUNT").sum())
            totals = int((row_types == "TOTAL").sum())

        #########################################################
        # Currency Detection
        #########################################################

        currency = ""

        if "currency" in dataframe.columns:

            values = dataframe["currency"].fillna("").astype(str).str.strip()

            values = values[values != ""]

            if not values.empty:

                currency = values.mode().iloc[0]

        #########################################################
        # Metadata
        #########################################################

        metadata = {
            "rows": row_count,
            "sections": sections,
            "subsections": subsections,
            "accounts": accounts,
            "totals": totals,
            "currency": currency,
        }

        return metadata

    # ==========================================================
    # SUMMARY
    # ==========================================================

    @classmethod
    def _build_summary(cls, document):

        dataframe = document.dataframe.copy()

        if dataframe.empty:
            return {}

        #########################################################
        # Keep ACCOUNT rows only
        #########################################################

        dataframe = dataframe[dataframe["row_type"].str.upper() == "ACCOUNT"].copy()

        if dataframe.empty:
            return {}

        #########################################################
        # Clean amount
        #########################################################

        dataframe["amount"] = (
            dataframe["amount"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .replace("", "0")
            .astype(float)
        )

        #########################################################
        # Build summary
        #########################################################

        summary = {}

        grouped = dataframe.groupby(["section", "subsection"], dropna=False)[
            "amount"
        ].sum()

        asset_total = 0
        liability_total = 0
        equity_total = 0

        for (section, subsection), amount in grouped.items():

            key = subsection.lower().replace("-", "_")
            key = key.replace(" ", "_")

            if section.lower() == "assets":

                summary[key] = amount
                asset_total += amount

            elif section.lower() == "liabilities":

                summary[key] = amount
                liability_total += amount

            elif section.lower() == "equity":

                equity_total += amount

        summary["total_assets"] = asset_total
        summary["total_liabilities"] = liability_total
        summary["total_equity"] = equity_total

        return summary

    # ==========================================================
    # TABLE
    # ==========================================================

    @staticmethod
    def _build_table(document):

        dataframe = document.dataframe

        if dataframe is None:
            return []

        dataframe = dataframe.fillna("")

        records = []

        for _, row in dataframe.iterrows():

            records.append(
                {
                    "row_type": str(row.get("row_type", "")),
                    "section": str(row.get("section", "")),
                    "subsection": str(row.get("subsection", "")),
                    "account_code": str(row.get("account_code", "")),
                    "account_name": str(row.get("account_name", "")),
                    "amount": str(row.get("amount", "")),
                    "currency": str(row.get("currency", "")),
                }
            )

        return records

    # ==========================================================
    # DOWNLOADS
    # ==========================================================

    @staticmethod
    def _build_downloads(document):

        return {
            "csv": document.csv_path,
            "excel": document.excel_path,
        }
