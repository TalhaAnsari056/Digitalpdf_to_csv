import re
import json

from config import OUTPUT_DIR
from models.balance_sheet_record import BalanceSheetRecord


class BalanceSheetAgent:

    SECTION_HEADERS = {
        "Current Assets",
        "Non-Current Assets",
        "Current Liabilities",
        "Non-Current Liabilities",
        "Equity",
    }

    @staticmethod
    def run(document):

        print("\nRunning Balance Sheet Parser...\n")

        current_section = ""

        parsed_records = []

        for row in document.rows:

            if not row.cells:
                continue

            row_text = " ".join(row.cells).strip()

            if row_text in BalanceSheetAgent.SECTION_HEADERS:

                current_section = row_text

                continue

            if len(row.cells) < 2:
                continue

            left = row.cells[0].strip()

            right = row.cells[-1].strip()

            amount = BalanceSheetAgent.parse_amount(right)

            code = ""

            account = left

            match = re.match(r"^(\d+)\s+(.*)", left)

            if match:

                code = match.group(1)

                account = match.group(2)

            parsed_records.append(
                BalanceSheetRecord(
                    page=row.page_number,
                    section=current_section,
                    account_code=code,
                    account_name=account,
                    amount=amount,
                )
            )

        document.parsed_data = parsed_records

        parsed_folder = OUTPUT_DIR / document.filename.replace(".pdf", "") / "parsed"

        parsed_folder.mkdir(parents=True, exist_ok=True)

        parsed_file = parsed_folder / "balance_sheet.json"

        data = []

        for record in parsed_records:

            data.append(
                {
                    "page": record.page,
                    "section": record.section,
                    "account_code": record.account_code,
                    "account_name": record.account_name,
                    "amount": record.amount,
                }
            )

        with open(parsed_file, "w", encoding="utf-8") as file:

            json.dump(data, file, indent=4)

        print(f"Parsed Records : {len(parsed_records)}")

        return document

    @staticmethod
    def parse_amount(value):

        value = value.replace(",", "")

        value = value.replace("(", "-")

        value = value.replace(")", "")

        try:
            return float(value)

        except:
            return 0.0
