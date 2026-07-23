import re
import pandas as pd


class BalancesheetNormalizerService:

    @classmethod
    def normalize(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize a parsed dataframe.

        This stage does NOT change the meaning of the data.
        It only standardizes formatting.
        """

        dataframe = dataframe.copy()

        dataframe = cls._expand_multiline_rows(dataframe)
        print("\n" + "=" * 70)
        print("AFTER MULTILINE EXPANSION")
        print("=" * 70)

        if {"account_code", "account_name", "amount"}.issubset(dataframe.columns):
            print(
                dataframe[["account_code", "account_name", "amount"]].to_string(
                    index=False
                )
            )

        print("=" * 70)

        dataframe = cls._normalize_empty_values(dataframe)
        dataframe = cls._trim_strings(dataframe)
        dataframe = cls._normalize_row_type(dataframe)
        dataframe = cls._normalize_account_code(dataframe)
        dataframe = cls._normalize_amount(dataframe)
        dataframe = cls._normalize_currency(dataframe)

        ####################################################
        # Remove duplicate rows produced by OCR/LLM
        ####################################################
        dataframe = dataframe.drop_duplicates(ignore_index=True)

        return dataframe.reset_index(drop=True)

    @staticmethod
    def _expand_multiline_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        Expand rows containing multiple logical records.

        Supports

        - <br>
        - <br/>
        - <BR>
        - newline

        Handles examples like

        account_code:
            1500

        account_name:
            Net Furniture...
            1600 Net Field Equipment

        amount:
            178309
            205741

        OR

        account_code:
            1500
            1600

        account_name:
            Furniture
            Field Equipment

        amount:
            178309
            205741

        The algorithm first repairs embedded account codes,
        then aligns every column.
        """

        expanded_rows = []

        splitter = re.compile(r"<br\s*/?>|\n", flags=re.IGNORECASE)

        for _, row in df.iterrows():

            row = row.copy()

            ###########################################################
            # Split every column
            ###########################################################

            split_columns = {}

            for column in df.columns:

                value = str(row[column]).strip()

                parts = [part.strip() for part in splitter.split(value) if part.strip()]

                if not parts:
                    parts = [""]

                split_columns[column] = parts

            ###########################################################
            # Repair embedded account codes BEFORE alignment
            ###########################################################

            if "account_name" in split_columns:

                names = split_columns["account_name"]

                codes = split_columns.get("account_code", [""])

                repaired_codes = []
                repaired_names = []

                for index, name in enumerate(names):

                    match = re.match(r"^(\d{3,})\s+(.+)$", name)

                    if match:

                        repaired_codes.append(match.group(1))
                        repaired_names.append(match.group(2).strip())

                    else:

                        if index < len(codes):
                            repaired_codes.append(codes[index])
                        elif len(codes) == 1:
                            repaired_codes.append(codes[0])
                        else:
                            repaired_codes.append("")

                        repaired_names.append(name)

                split_columns["account_code"] = repaired_codes
                split_columns["account_name"] = repaired_names

            ###########################################################
            # Determine final number of logical rows
            ###########################################################

            max_parts = max(len(parts) for parts in split_columns.values())

            ###########################################################
            # Expand
            ###########################################################

            for i in range(max_parts):

                new_row = {}

                for column in df.columns:

                    parts = split_columns[column]

                    if len(parts) == max_parts:

                        value = parts[i]

                    elif len(parts) == 1:

                        value = parts[0]

                    elif i < len(parts):

                        value = parts[i]

                    else:

                        value = ""

                    new_row[column] = value
                print(
                    f"{new_row.get('account_code')} | "
                    f"{new_row.get('account_name')} | "
                    f"{new_row.get('amount')}"
                )
                expanded_rows.append(new_row)

        return pd.DataFrame(expanded_rows).reset_index(drop=True)

    # ==========================================================
    # EMPTY VALUES
    # ==========================================================

    @staticmethod
    def _normalize_empty_values(dataframe: pd.DataFrame) -> pd.DataFrame:

        dataframe = dataframe.fillna("")

        return dataframe

    # ==========================================================
    # TRIM ALL STRINGS
    # ==========================================================

    @staticmethod
    def _trim_strings(dataframe: pd.DataFrame) -> pd.DataFrame:

        for column in dataframe.columns:

            dataframe[column] = (
                dataframe[column]
                .astype(str)
                .str.replace("\u00a0", " ", regex=False)
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

        dataframe["row_type"] = dataframe["row_type"].str.upper().str.strip()

        return dataframe

    # ==========================================================
    # ACCOUNT CODE
    # ==========================================================

    @staticmethod
    def _normalize_account_code(dataframe: pd.DataFrame) -> pd.DataFrame:

        if "account_code" not in dataframe.columns:
            return dataframe

        dataframe["account_code"] = (
            dataframe["account_code"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        return dataframe

    # ==========================================================
    # AMOUNT
    # ==========================================================

    @classmethod
    def _normalize_amount(cls, dataframe: pd.DataFrame) -> pd.DataFrame:

        if "amount" not in dataframe.columns:
            return dataframe

        dataframe["amount"] = dataframe["amount"].apply(cls._clean_amount)

        return dataframe

    @staticmethod
    def _clean_amount(value: str) -> str:

        if value is None:
            return ""

        value = str(value).strip()

        if value == "":
            return ""

        value = value.replace(",", "")

        # (125000) -> -125000
        if re.fullmatch(r"\(.*\)", value):

            value = "-" + value[1:-1].strip()

        value = value.replace("$", "")
        value = value.replace("€", "")
        value = value.replace("£", "")
        value = value.replace("PKR", "")
        value = value.replace("USD", "")

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
