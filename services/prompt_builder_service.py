class PromptBuilderService:

    @staticmethod
    def build(document):

        if document.document_type == "balance_sheet":
            return PromptBuilderService.build_balance_sheet_prompt(
                document.cleaned_markdown
            )

        elif document.document_type == "bank_statement":
            return PromptBuilderService.build_bank_statement_prompt(
                document.cleaned_markdown
            )

        raise ValueError(f"Unsupported document type: {document.document_type}")

    # ==========================================================
    # BALANCE SHEET
    # ==========================================================

    @staticmethod
    def build_balance_sheet_prompt(markdown: str):

        return f"""
You are an expert financial statement normalization engine.

Your task is NOT to summarize.

Your task is to convert the provided balance sheet into ONE standardized Markdown table.

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return EXACTLY ONE markdown table.

Do NOT return JSON.

Do NOT explain anything.

Do NOT wrap the table inside markdown code fences.

Do NOT add any text before or after the table.

--------------------------------------------------
COLUMN NAMES
--------------------------------------------------

Use EXACTLY these columns.

| section | account_code | account_name | amount | currency |

--------------------------------------------------
MAPPING RULES
--------------------------------------------------
- LINE-BY-LINE EXTRACTION: Extract every single financial line. If a row has text and a number, it MUST be in the output table.
- NO ACCOUNT CODES? If the document does not use numbering/account codes, strictly leave the 'account_code' column completely empty. Do NOT invent codes.
- HANDLING SUB-HEADINGS: Do not skip rows that are just headings or sub-totals (e.g., "Total Current Assets"). Map them with an empty 'account_code'.
- SINGLE YEAR ASSIGNMENT: If multiple columns of figures exist for different years, extract the values for the LATEST year only.
- Convert every account into one row.
- Preserve the original row order.
- Preserve all numeric values exactly.
- Preserve negative values.
- Preserve decimal values.
- Preserve currency symbols if available.
- Never invent values.
- Never calculate totals.
- Never merge rows.
- Never split rows.
- If a value is unavailable, leave the cell empty.
- Standardize section names where possible
  (Assets, Liabilities, Equity).

--------------------------------------------------
DOCUMENT
--------------------------------------------------

{markdown}
"""

    # ==========================================================
    # BANK STATEMENT
    # ==========================================================

    @staticmethod
    def build_bank_statement_prompt(markdown: str):

        return f"""
You are an expert bank statement normalization engine.

Your task is NOT to summarize.

Your task is to convert the statement into ONE standardized Markdown table.

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return EXACTLY ONE markdown table.

Do NOT return JSON.

Do NOT explain anything.

Do NOT wrap the table inside markdown code fences.

Do NOT add any text before or after the table.

--------------------------------------------------
COLUMN NAMES
--------------------------------------------------

Use EXACTLY these columns.

| date | description | reference | debit | credit | balance | currency |

--------------------------------------------------
MAPPING RULES
--------------------------------------------------

- Preserve transaction order.
- Preserve every transaction.
- Preserve dates exactly.
- Preserve numeric values exactly.
- Preserve negative values.
- Preserve decimal values.
- Preserve currency if available.
- Never invent transactions.
- Never merge transactions.
- Never split transactions.
- If a value is unavailable, leave the cell empty.

--------------------------------------------------
EXAMPLE
--------------------------------------------------

| date | description | reference | debit | credit | balance | currency |
| ---- | ----------- | --------- | ----- | ------ | ------- | -------- |
| 01/01/2025 | ATM Withdrawal | ATM123 | 500 | | 1500 | PKR |
| 02/01/2025 | Salary | SAL001 | | 50000 | 51500 | PKR |

--------------------------------------------------
DOCUMENT
--------------------------------------------------

{markdown}
"""
