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

Your ONLY task is to normalize the financial statement into ONE standardized markdown table for automated parsing.

You are NOT summarizing.

You are NOT interpreting.

You are NOT calculating.

You are NOT improving formatting.

You are ONLY extracting structured data.

==================================================
OUTPUT
==================================================

Return EXACTLY ONE markdown table.

Do NOT return JSON.

Do NOT explain anything.

Do NOT use markdown code fences.

Do NOT output any text before or after the table.

==================================================
OUTPUT SCHEMA
==================================================

Use EXACTLY these columns.

| row_type | section | subsection | account_code | account_name | amount | currency |

Do NOT add or remove columns.

==================================================
ROW TYPES
==================================================

Every row MUST be exactly ONE of these types.

SECTION
SUBSECTION
ACCOUNT
TOTAL

==================================================
SECTION
==================================================

Represents the highest financial category.

Examples

Assets
Liabilities
Equity

Rules

- section contains the section name.
- subsection is empty.
- account_code is empty.
- account_name is empty.
- amount is empty.
- currency is empty.

Exactly ONE SECTION row should be emitted when a new top-level section begins.

==================================================
SUBSECTION
==================================================

Represents a grouping inside a section.

Examples

Current Assets
Non-Current Assets
Current Liabilities
Non-Current Liabilities

Rules

- section contains the parent section.
- subsection contains the subsection name.
- account_code is empty.
- account_name is empty.
- amount is empty.
- currency is empty.

Create exactly ONE SUBSECTION row.

The subsection row must NEVER contain the first account.

The first account after a subsection MUST become its own ACCOUNT row.

==================================================
ACCOUNT
==================================================

Represents a real financial account.

Examples

Cash
Checking
Inventory
Accounts Receivable
Equipment
Retained Earnings

Rules

- Repeat the current section.
- Repeat the current subsection if one exists.
- account_name contains ONLY the account name.
- account_code contains ONLY the account code if present.
- amount contains ONLY the account amount.
- currency contains the currency if shown.

Never place subsection names inside account_name.

Never merge an account into a subsection row.

Never combine multiple accounts into one row.

Every ACCOUNT row represents exactly ONE account.

==================================================
TOTAL
==================================================

Represents subtotal or total rows.

Examples

Total Current Assets
Total Assets
Total Liabilities
Total Equity
Total Liabilities and Equity

Rules

- Repeat the current section.
- Repeat the current subsection if applicable.
- account_code is empty.
- account_name contains the total label exactly as written.
- amount contains the reported value.

Never calculate totals.

Never invent totals.

==================================================
GENERAL EXTRACTION RULES
==================================================

Extract EVERY financial row.

Never skip rows.

Never omit rows.

Never invent rows.

Preserve the original document order.

Preserve every numeric value exactly.

Preserve negative values.

Preserve decimal values.

Preserve currency symbols.

If account codes do not exist, leave account_code empty.

If amount does not exist, leave amount empty.

If currency does not exist, leave currency empty.

If multiple reporting years exist, extract ONLY the latest year.

If one OCR line contains multiple accounts, split them into separate ACCOUNT rows.

Never place multiple account names into one row.

Never place multiple account codes into one row.

Never use HTML tags.

Never use <br>.

==================================================
HIERARCHY
==================================================

Think of the document as a hierarchy.

SECTION
    ↓
SUBSECTION (optional)
    ↓
ACCOUNT
    ↓
TOTAL

Each row belongs to exactly ONE level.

Do NOT merge two levels into one row.

==================================================
EXAMPLE
==================================================

| row_type | section | subsection | account_code | account_name | amount | currency |
|----------|---------|------------|--------------|--------------|--------|----------|
| SECTION | Assets | | | | | |
| SUBSECTION | Assets | Current Assets | | | | |
| ACCOUNT | Assets | Current Assets | 1000 | Cash | 898402 | |
| ACCOUNT | Assets | Current Assets | 1010 | Checking | 583961 | |
| ACCOUNT | Assets | Current Assets | 1020 | Savings | 224600 | |
| ACCOUNT | Assets | Current Assets | 1030 | Petty Cash | 89840 | |
| ACCOUNT | Assets | Current Assets | 1100 | Accounts Receivable | 3593607 | |
| TOTAL | Assets | Current Assets | | Total Current Assets | 5356121 | |
| SUBSECTION | Assets | Non-Current Assets | | | | |
| ACCOUNT | Assets | Non-Current Assets | 1400 | Net Computer Equipment | 185167 | |
| ACCOUNT | Assets | Non-Current Assets | 1500 | Net Furniture, Fixtures, & Equipment | 178309 | |
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
You are an expert financial document normalization engine.

The input is a CLEAN MARKDOWN extracted from a DIGITAL BANK STATEMENT.

Your task is to convert it into ONE standardized markdown table.

Return ONLY the markdown table.

Do NOT return JSON.

Do NOT explain anything.

Do NOT use code fences.

------------------------------------------------------------
OUTPUT SCHEMA
------------------------------------------------------------

Use EXACTLY these columns.

| row_type | date | description | debit | credit | balance | currency |

------------------------------------------------------------
VALID ROW TYPES
------------------------------------------------------------

OPENING_BALANCE

TRANSACTION

CLOSING_BALANCE

SUMMARY

------------------------------------------------------------
GENERAL RULES
------------------------------------------------------------

Every markdown row represents EXACTLY ONE logical record.

Preserve the original transaction order.

Never reorder transactions.

Never merge two transactions.

Never split one transaction into multiple transactions.

Never duplicate any transaction.

Never invent any transaction.

Never invent any amount.

Never invent any balance.

Never invent any date.

Never invent any currency.

Leave unavailable fields empty.

------------------------------------------------------------
DESCRIPTION RULES
------------------------------------------------------------

Many bank statements wrap long descriptions across multiple physical lines.

Those wrapped lines belong to ONE transaction.

Join wrapped lines into ONE description separated by spaces.

Do NOT keep line breaks.

Do NOT insert <br>.

Do NOT repeat words.

Do NOT move description text to another transaction.

Every description must belong only to its own transaction.

------------------------------------------------------------
DATE RULES
------------------------------------------------------------

Some dates are split across lines.

Example

04-Aug
2023

Output

2023-08-04

If the full year is available elsewhere in that same logical row,
combine it correctly.

If a complete date cannot be determined,
preserve exactly what exists.

------------------------------------------------------------
NUMERIC RULES
------------------------------------------------------------

Preserve numeric values exactly.

Preserve decimals.

Preserve negative values.

Do not round.

Do not recalculate balances.

Do not modify amounts.

------------------------------------------------------------
OPENING / CLOSING BALANCE RULES
------------------------------------------------------------

Only output an OPENING_BALANCE row if it actually exists.

Only output a CLOSING_BALANCE row if it explicitly exists in the document.

Never invent either one.

------------------------------------------------------------
SUMMARY RULES
------------------------------------------------------------

Only output SUMMARY rows if the document explicitly contains summary information.

Otherwise do not create SUMMARY rows.

------------------------------------------------------------
CURRENCY RULES
------------------------------------------------------------

If currency is explicitly available for a transaction or document,
copy it.

Otherwise leave the currency column empty.

Never guess the currency.

------------------------------------------------------------
MISSING VALUES
------------------------------------------------------------

If Debit is missing,
leave Debit empty.

If Credit is missing,
leave Credit empty.

If Balance is missing,
leave Balance empty.

Never replace missing values with 0.

------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

The output must contain ONLY the markdown table.

Nothing before it.

Nothing after it.

------------------------------------------------------------
DOCUMENT
------------------------------------------------------------
   
{markdown}
"""


# You are an expert bank statement normalization engine.

# Convert the document into ONE standardized markdown table.

# Return ONLY the markdown table.

# Do NOT return JSON.

# Do NOT explain anything.

# Do NOT use code fences.

# Use EXACTLY these columns.

# | row_type | date | description | debit | credit | balance | currency |

# Row types may include

# OPENING_BALANCE

# TRANSACTION

# CLOSING_BALANCE

# SUMMARY

# Rules

# - Preserve transaction order.
# - Preserve every transaction.
# - Never invent transactions.
# - Never merge transactions.
# - Never split transactions.
# - Every markdown row represents exactly ONE logical record.
# - Preserve dates exactly.
# - Preserve numeric values exactly.
# - Preserve negative values.
# - Preserve decimals.
# - Preserve currency.
# - Leave unavailable fields empty.

# DOCUMENT
