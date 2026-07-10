import re
import json

from config import OUTPUT_DIR
from models.bank_statement_record import BankStatementRecord


class BankStatementAgent:

    DATE_PATTERN = re.compile(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}")

    AMOUNT_PATTERN = re.compile(r"-?\(?[\d,]+\.\d+\)?")

    CURRENCY_PATTERN = re.compile(
        r"\b(PKR|USD|EUR|GBP|AED|SAR)\b",
        re.IGNORECASE,
    )

    @staticmethod
    def run(document):

        print("\nRunning Bank Statement Parser...\n")

        transaction_blocks = []

        current_block = []

        # ----------------------------------------
        # Build Transaction Blocks
        # ----------------------------------------

        for row in document.rows:

            row_text = " ".join(row.cells) if row.cells else row.text

            row_text = row_text.strip()

            if not row_text:
                continue

            if BankStatementAgent.DATE_PATTERN.search(row_text):

                if current_block:
                    transaction_blocks.append(current_block)

                current_block = [row]

            else:

                if current_block:
                    current_block.append(row)

        if current_block:
            transaction_blocks.append(current_block)

        # ----------------------------------------
        # Parse Transaction Blocks
        # ----------------------------------------

        parsed_records = []

        for block in transaction_blocks:

            page = block[0].page_number

            block_cells = []

            for row in block:

                if row.cells:
                    block_cells.extend(row.cells)
                else:
                    block_cells.append(row.text)

            block_text = " ".join(block_cells)

            date = ""

            currency = ""

            debit = None

            credit = None

            balance = None

            description_parts = []

            date_match = BankStatementAgent.DATE_PATTERN.search(block_text)

            if date_match:
                date = date_match.group()

            currency_match = BankStatementAgent.CURRENCY_PATTERN.search(block_text)

            if currency_match:
                currency = currency_match.group().upper()

            amounts = []

            for match in BankStatementAgent.AMOUNT_PATTERN.finditer(block_text):

                value = BankStatementAgent.parse_amount(match.group())

                if value is not None:
                    amounts.append(value)

            for cell in block_cells:

                if date and date in cell:
                    continue

                if currency and currency in cell.upper():
                    continue

                if BankStatementAgent.AMOUNT_PATTERN.fullmatch(cell):
                    continue

                description_parts.append(cell)

            description = " ".join(description_parts)

            description = re.sub(r"\s+", " ", description).strip()

            if len(amounts) >= 1:
                debit = amounts[0]

            if len(amounts) >= 2:
                balance = amounts[-1]

            parsed_records.append(
                BankStatementRecord(
                    page=page,
                    date=date,
                    description=description,
                    debit=debit,
                    credit=credit,
                    balance=balance,
                    currency=currency,
                )
            )

        document.parsed_data = parsed_records

        # ----------------------------------------
        # Save Parsed Output
        # ----------------------------------------

        parsed_folder = OUTPUT_DIR / document.filename.replace(".pdf", "") / "parsed"

        parsed_folder.mkdir(parents=True, exist_ok=True)

        parsed_file = parsed_folder / "bank_statement.json"

        data = []

        for record in parsed_records:

            data.append(
                {
                    "page": record.page,
                    "date": record.date,
                    "description": record.description,
                    "debit": record.debit,
                    "credit": record.credit,
                    "balance": record.balance,
                    "currency": record.currency,
                }
            )

        with open(parsed_file, "w", encoding="utf-8") as file:

            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"Transaction Blocks : {len(transaction_blocks)}")

        print(f"Parsed Records     : {len(parsed_records)}")

        return document

    @staticmethod
    def parse_amount(value):

        value = value.replace(",", "")

        value = value.replace("(", "-")

        value = value.replace(")", "")

        try:
            return float(value)

        except:
            return None
