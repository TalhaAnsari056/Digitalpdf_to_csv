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
You are a financial data extraction engine.

Extract EVERY financial line item from the balance sheet into a simple two-column format.

Return EXACTLY this markdown table structure:

| account_name | amount |
|-------------|--------|
| [name] | [value] |

RULES:
1. Extract EVERY single line - do not skip any rows
2. Include ALL of these types of rows:
   - Account codes with names (e.g., "1000 Cash", "1100 Accounts Receivable")
   - Subtotal lines (e.g., "Total Cash", "Total Current Assets")
   - Section headers (e.g., "Current Assets", "Non-Current Assets")
   - Main categories (e.g., "Assets", "Liabilities", "Equity")
3. Preserve the exact hierarchy and order from the original document
4. Keep account codes as part of the account_name if present
5. For rows with multiple accounts (like "1500 Net Furniture, Fixtures, & Equipment 1600 Net Field Equipment"), split them into separate rows
6. Preserve all amounts exactly as shown - including commas, parentheses for negatives, and decimals
7. Leave amount blank if no value is present
8. Do not calculate or modify any values
9. Do not skip empty rows that represent structural elements
10. Output ONLY the markdown table - no explanations, no code fences

EXAMPLE OUTPUT:
| account_name | amount |
|-------------|--------|
| Assets | |
| Current Assets | |
| 1000 Cash | |
| 1010 Checking | 583,961 |
| 1020 Savings | 224,600 |
| 1030 Petty Cash | 89,840 |
| Total Cash | 898,402 |
| 1100 Accounts Receivable | 3,593,607 |
| 1200 Work in Process | 589,791 |
| 1300 Other Current Assets | |
| 1310 Prepaid Rent | 164,593 |
| 1320 Prepaid Liability Insurance | 109,728 |
| Total Other Current Assets | 274,321 |
| Total Current Assets | 5,356,121 |

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
