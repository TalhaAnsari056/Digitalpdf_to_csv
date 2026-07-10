class ClassifierService:

    BANK_KEYWORDS = [
        "statement",
        "transaction",
        "account",
        "balance",
        "withdrawal",
        "deposit",
        "currency",
        "iban",
        "credit",
        "debit",
    ]

    BALANCE_KEYWORDS = [
        "assets",
        "liabilities",
        "equity",
        "balance sheet",
        "current assets",
        "current liabilities",
        "retained earnings",
        "capital",
        "total assets",
    ]

    @classmethod
    def classify(cls, document):

        text = ""

        for page in document.pages:

            text += page.text.lower()

            text += "\n"

        bank_score = 0

        balance_score = 0

        for keyword in cls.BANK_KEYWORDS:

            bank_score += text.count(keyword)

        for keyword in cls.BALANCE_KEYWORDS:

            balance_score += text.count(keyword)

        print("Bank Score :", bank_score)

        print("Balance Score :", balance_score)

        if bank_score > balance_score:

            return "bank_statement"

        return "balance_sheet"
