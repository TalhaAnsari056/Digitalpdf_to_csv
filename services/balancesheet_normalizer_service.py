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
    Split rows that contain multiple logical records separated by <br>.

    Handles examples like:

    account_code:
        1500<br>1600

    account_name:
        Cash<br>Bank

    amount:
        100<br>200

    OR

    account_code:
        1500

    account_name:
        Net Furniture...<br>1600 Net Field Equipment

    amount:
        178309<br>205741

    Also supports OCR outputs that contain:
        <br>
        <br/>
        <BR>
        newline characters

    without changing the meaning of the data.
    """

    rows = []

    for _, row in df.iterrows():

        row = row.copy()

        ############################################################
        # Split every column
        ############################################################

        split_columns = {}
        max_parts = 1

        for column in df.columns:

            value = str(row[column]).strip()

            parts = [
                part.strip()
                for part in re.split(r"<br\s*/?>|\n", value, flags=re.IGNORECASE)
                if part.strip()
            ]

            if not parts:
                parts = [""]

            split_columns[column] = parts
            max_parts = max(max_parts, len(parts))

        ############################################################
        # Normal row
        ############################################################

        if max_parts == 1:
            rows.append(row)
            continue

        ############################################################
        # Expand into multiple logical rows
        ############################################################

        for index in range(max_parts):

            new_row = row.copy()

            for column in df.columns:

                parts = split_columns[column]

                if len(parts) == max_parts:
                    value = parts[index]

                elif len(parts) == 1:
                    value = parts[0]

                else:
                    value = ""

                new_row[column] = value

            ########################################################
            # Detect embedded account code
            #
            # Example:
            #
            # 1600 Net Field Equipment
            #
            # Override inherited account code if present.
            ########################################################

            name = str(new_row.get("account_name", "")).strip()

            match = re.match(r"^(\d{3,})\s+(.+)$", name)

            if match:

                new_row["account_code"] = match.group(1)
                new_row["account_name"] = match.group(2).strip()

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
