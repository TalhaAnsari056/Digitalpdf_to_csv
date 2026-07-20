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
        Split rows where the LLM packed multiple accounts into one row.

        Handles cases like:

        account_code:
            1500<br>1600

        account_name:
            Cash<br>Bank

        amount:
            100<br>200

        OR

        account_name:
            1500 Cash<br>1600 Bank

        amount:
            100<br>200

        Works for any future PDF that follows the same pattern.
        """

        rows = []

        for _, row in df.iterrows():

            row = row.copy()

            ############################################################
            # Split every column on <br>
            ############################################################

            split_columns = {}

            max_parts = 1

            for col in df.columns:

                value = str(row[col]).strip()

                parts = [p.strip() for p in re.split(r"<br\s*/?>", value) if p.strip()]

                split_columns[col] = parts

                max_parts = max(max_parts, len(parts))

            ############################################################
            # Normal row
            ############################################################

            if max_parts == 1:
                rows.append(row)
                continue

            ############################################################
            # Expand into multiple rows
            ############################################################

            for i in range(max_parts):

                new_row = row.copy()

                for col in df.columns:

                    parts = split_columns[col]

                    if len(parts) == max_parts:
                        value = parts[i]

                    elif len(parts) == 1:
                        value = parts[0]

                    else:
                        value = ""

                    new_row[col] = value

                ########################################################
                # Detect embedded account code
                #
                # Example:
                # 1600 Net Field Equipment
                #
                # This works whether account_code is empty
                # OR incorrectly inherited from the previous row.
                ########################################################

            name = str(new_row.get("account_name", "")).strip()

            match = re.match(r"^(\d{3,})\s+(.+)$", name)

            if match:

                embedded_code = match.group(1)
                embedded_name = match.group(2).strip()

                new_row["account_code"] = embedded_code
                new_row["account_name"] = embedded_name

                rows.append(new_row)

        return pd.DataFrame(rows).reset_index(drop=True)

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
