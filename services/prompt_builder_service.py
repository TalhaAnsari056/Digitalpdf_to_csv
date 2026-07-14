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
You are an expert financial document extraction engine.

Your task is to extract every field from the balance sheet.

STRICT RULES

1. Return ONLY valid JSON.
2. Do NOT explain anything.
3. Do NOT wrap JSON inside markdown.
4. Do NOT add comments.
5. Missing values must be null.
6. Never invent values.
7. Preserve negative numbers.
8. Preserve decimal values exactly.
9. Preserve currency symbols if present.
10. Return every row appearing in the table.

Expected JSON structure:

{{
    "company_name": "",
    "report_date": "",
    "currency": "",
    "assets": [],
    "liabilities": [],
    "equity": [],
    "totals": {{}}
}}

Document:

{markdown}
"""

    # ==========================================================
    # BANK STATEMENT
    # ==========================================================

    @staticmethod
    def build_bank_statement_prompt(markdown: str):

        return f"""
You are an expert bank statement extraction engine.

Extract every transaction from the statement.

STRICT RULES

1. Return ONLY valid JSON.
2. Do NOT explain.
3. Do NOT use markdown.
4. Missing values must be null.
5. Never invent data.
6. Preserve dates exactly.
7. Preserve decimal values exactly.
8. Preserve negative values.
9. Preserve transaction order.

Expected JSON structure:

{{
    "bank_name": "",
    "account_number": "",
    "account_holder": "",
    "currency": "",
    "opening_balance": "",
    "closing_balance": "",
    "transactions": []
}}

Document:

{markdown}
"""
