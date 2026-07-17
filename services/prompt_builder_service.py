# class PromptBuilderService:

#     @staticmethod
#     def build(document):

#         if document.document_type == "balance_sheet":
#             return PromptBuilderService.build_balance_sheet_prompt(
#                 document.cleaned_markdown
#             )

#         elif document.document_type == "bank_statement":
#             return PromptBuilderService.build_bank_statement_prompt(
#                 document.cleaned_markdown
#             )

#         raise ValueError(f"Unsupported document type: {document.document_type}")

#     # ==========================================================
#     # BALANCE SHEET
#     # ==========================================================

#     @staticmethod
#     def build_balance_sheet_prompt(markdown: str):

#         return f"""
# You are an expert financial statement normalization engine.

# Your task is NOT to summarize.

# Your task is to convert the provided balance sheet into ONE standardized Markdown table.

# --------------------------------------------------
# OUTPUT FORMAT
# --------------------------------------------------

# Return EXACTLY ONE markdown table.

# Do NOT return JSON.

# Do NOT explain anything.

# Do NOT wrap the table inside markdown code fences.

# Do NOT add any text before or after the table.

# --------------------------------------------------
# COLUMN NAMES
# --------------------------------------------------

# Use EXACTLY these columns.

# | section | account_code | account_name | amount | currency |

# --------------------------------------------------
# MAPPING RULES
# --------------------------------------------------
# - LINE-BY-LINE EXTRACTION: Extract every single financial line. If a row has text and a number, it MUST be in the output table.
# - NO ACCOUNT CODES? If the document does not use numbering/account codes, strictly leave the 'account_code' column completely empty. Do NOT invent codes.
# - HANDLING SUB-HEADINGS: Do not skip rows that are just headings or sub-totals (e.g., "Total Current Assets"). Map them with an empty 'account_code'.
# - SINGLE YEAR ASSIGNMENT: If multiple columns of figures exist for different years, extract the values for the LATEST year only.
# - Convert every account into one row.
# - Preserve the original row order.
# - Preserve all numeric values exactly.
# - Preserve negative values.
# - Preserve decimal values.
# - Preserve currency symbols if available.
# - Never invent values.
# - Never calculate totals.
# - Never merge rows.
# - Never split rows.
# - If a value is unavailable, leave the cell empty.
# - Standardize section names where possible
#   (Assets, Liabilities, Equity).

# --------------------------------------------------
# DOCUMENT
# --------------------------------------------------

# {markdown}
# """

#     # ==========================================================
#     # BANK STATEMENT
#     # ==========================================================

#     @staticmethod
#     def build_bank_statement_prompt(markdown: str):

#         return f"""
# You are an expert bank statement normalization engine.

# Your task is NOT to summarize.

# Your task is to convert the statement into ONE standardized Markdown table.

# --------------------------------------------------
# OUTPUT FORMAT
# --------------------------------------------------

# Return EXACTLY ONE markdown table.

# Do NOT return JSON.

# Do NOT explain anything.

# Do NOT wrap the table inside markdown code fences.

# Do NOT add any text before or after the table.

# --------------------------------------------------
# COLUMN NAMES
# --------------------------------------------------

# Use EXACTLY these columns.

# | date | description | reference | debit | credit | balance | currency |

# --------------------------------------------------
# MAPPING RULES
# --------------------------------------------------

# - Preserve transaction order.
# - Preserve every transaction.
# - Preserve dates exactly.
# - Preserve numeric values exactly.
# - Preserve negative values.
# - Preserve decimal values.
# - Preserve currency if available.
# - Never invent transactions.
# - Never merge transactions.
# - Never split transactions.
# - If a value is unavailable, leave the cell empty.

# --------------------------------------------------
# DOCUMENT
# --------------------------------------------------


# {markdown}
# """
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

Your ONLY job is to normalize the document into ONE standardized markdown table.

You are NOT summarizing.

You are NOT interpreting.

You are NOT calculating.

You are NOT reformatting for humans.

You are producing structured data for an automated parser.

==================================================
OUTPUT RULES
==================================================

Return EXACTLY ONE markdown table.

Do NOT return JSON.

Do NOT explain anything.

Do NOT wrap inside ```.

Do NOT output any text before the table.

Do NOT output any text after the table.

==================================================
OUTPUT SCHEMA
==================================================

Use EXACTLY these columns.

| row_type | section | subsection | account_code | account_name | amount | currency |

==================================================
ROW TYPE
==================================================

Every row MUST belong to exactly ONE of these types.

SECTION

SUBSECTION

ACCOUNT

TOTAL

==================================================
SECTION
==================================================

SECTION represents the highest financial category.

Examples

Assets

Liabilities

Equity

Only SECTION rows populate the section column.

==================================================
SUBSECTION
==================================================

SUBSECTION represents a grouping inside a section.

Examples

Current Assets

Non-Current Assets

Current Liabilities

Long-Term Liabilities

Only SUBSECTION rows populate the subsection column.

Do NOT place subsection names inside account_name.

==================================================
ACCOUNT
==================================================

ACCOUNT rows represent actual ledger accounts.

Examples

Cash

Checking

Savings

Accounts Receivable

Inventory

Retained Earnings

Only ACCOUNT rows may contain an account_code.

If the source document has no account code,

leave account_code empty.

==================================================
TOTAL
==================================================

TOTAL rows represent subtotal or total rows.

Examples

Total Current Assets

Total Assets

Total Liabilities

Total Equity

Total Liabilities and Equity

TOTAL rows never contain account codes.

==================================================
IMPORTANT RULES
==================================================

Extract EVERY financial row.

Never skip rows.

Preserve original order.

Never invent values.

Never calculate totals.

Never merge rows.

Never merge accounts.

Never split one account across multiple rows.

If two accounts appear on the same OCR line,

create TWO markdown rows.

Never use <br>.

Never place two account codes in one row.

Never place two account names in one row.

Every markdown row must represent exactly ONE logical record.

If account code does not exist,

leave it blank.

If amount does not exist,

leave it blank.

If currency does not exist,

leave it blank.

If multiple years are present,

extract ONLY the latest year.

Preserve every numeric value exactly.

Preserve negative values.

Preserve decimal values.

Preserve currency symbols.

==================================================
GOOD EXAMPLE
==================================================

| row_type | section | subsection | account_code | account_name | amount | currency |
|----------|----------|------------|--------------|--------------|--------|----------|
| SECTION | Assets | | | | | |
| SUBSECTION | Assets | Current Assets | | | | |
| ACCOUNT | Assets | Current Assets | 1000 | Cash | 898402 | |
| ACCOUNT | Assets | Current Assets | 1010 | Checking | 583961 | |
| ACCOUNT | Assets | Current Assets | 1020 | Savings | 224600 | |
| TOTAL | Assets | Current Assets | | Total Current Assets | 5356121 | |
| SUBSECTION | Assets | Non-Current Assets | | | | |
| ACCOUNT | Assets | Non-Current Assets | 1400 | Equipment | 185167 | |
| TOTAL | Assets | Non-Current Assets | | Total Non-Current Assets | 1501908 | |
| TOTAL | Assets | | | Total Assets | 6858029 | |

==================================================
DOCUMENT
==================================================

{markdown}
"""

    # ==========================================================
    # BANK STATEMENT
    # ==========================================================

    @staticmethod
    def build_bank_statement_prompt(markdown: str):

        return f"""
You are an expert bank statement normalization engine.

Convert the document into ONE standardized markdown table.

Return ONLY the markdown table.

Do NOT return JSON.

Do NOT explain anything.

Do NOT use code fences.

Use EXACTLY these columns.

| row_type | date | description | reference | debit | credit | balance | currency |

Row types may include

OPENING_BALANCE

TRANSACTION

CLOSING_BALANCE

SUMMARY

Rules

- Preserve transaction order.
- Preserve every transaction.
- Never invent transactions.
- Never merge transactions.
- Never split transactions.
- Every markdown row represents exactly ONE logical record.
- Preserve dates exactly.
- Preserve numeric values exactly.
- Preserve negative values.
- Preserve decimals.
- Preserve currency.
- Leave unavailable fields empty.

DOCUMENT

{markdown}
"""
