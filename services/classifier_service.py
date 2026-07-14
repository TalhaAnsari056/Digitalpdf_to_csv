class ClassifierService:

    BANK_KEYWORDS = [
        "statement",
        "transaction",
        "transactions",
        "account",
        "account number",
        "account no",
        "opening balance",
        "closing balance",
        "deposit",
        "withdrawal",
        "debit",
        "credit",
        "value date",
        "posting date",
        "description",
        "reference",
        "balance",
        "available balance",
        "iban",
        "swift",
    ]

    BALANCE_KEYWORDS = [
        "balance sheet",
        "assets",
        "current assets",
        "non-current assets",
        "fixed assets",
        "liabilities",
        "current liabilities",
        "non-current liabilities",
        "equity",
        "share capital",
        "retained earnings",
        "capital",
        "inventory",
        "cash and cash equivalents",
        "accounts receivable",
        "accounts payable",
        "total assets",
        "total liabilities",
        "total equity",
    ]

    @classmethod
    def classify(cls, document):

        text = document.cleaned_markdown.lower()

        bank_score = 0
        balance_score = 0

        print("\n========== CLASSIFICATION ==========\n")

        print("Bank Keyword Matches")

        for keyword in cls.BANK_KEYWORDS:

            count = text.count(keyword)

            if count:

                print(f"{keyword:<30} {count}")

            bank_score += count

        print()

        print("Balance Sheet Keyword Matches")

        for keyword in cls.BALANCE_KEYWORDS:

            count = text.count(keyword)

            if count:

                print(f"{keyword:<30} {count}")

            balance_score += count

        print()

        print(f"Bank Score          : {bank_score}")
        print(f"Balance Sheet Score : {balance_score}")
        print()

        if bank_score > balance_score:

            return "bank_statement"

        return "balance_sheet"
