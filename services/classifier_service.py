import re


class ClassifierService:

    # ==========================================================
    # BANK STATEMENT KEYWORDS
    # ==========================================================

    BANK_KEYWORDS = {
        "statement": 2,
        "transaction": 3,
        "transactions": 3,
        "account": 2,
        "account number": 3,
        "opening balance": 5,
        "closing balance": 5,
        "deposit": 3,
        "withdrawal": 3,
        "debit": 4,
        "credit": 4,
        "value date": 4,
        "posting date": 4,
        "reference": 2,
        "available balance": 5,
        "iban": 5,
        "swift": 5,
    }

    # ==========================================================
    # BALANCE SHEET KEYWORDS
    # ==========================================================

    BALANCE_KEYWORDS = {
        "balance sheet": 6,
        "assets": 4,
        "current assets": 5,
        "non current assets": 5,
        "fixed assets": 5,
        "liabilities": 4,
        "current liabilities": 5,
        "non current liabilities": 5,
        "equity": 4,
        "share capital": 5,
        "retained earnings": 5,
        "inventory": 3,
        "cash and cash equivalents": 5,
        "accounts receivable": 4,
        "accounts payable": 4,
        "total assets": 6,
        "total liabilities": 6,
        "total equity": 6,
    }

    # ==========================================================

    @staticmethod
    def normalize(text: str) -> str:

        text = text.lower()

        text = text.replace("|", " ")

        text = re.sub(r"\s+", " ", text)

        return text

    # ==========================================================

    @classmethod
    def calculate_score(cls, text, keywords, title):

        score = 0

        print(title)
        print("-" * len(title))

        for keyword, weight in keywords.items():

            count = text.count(keyword)

            if count:

                subtotal = count * weight

                score += subtotal

                print(
                    f"{keyword:<35}"
                    f"count={count:<3}"
                    f"weight={weight:<2}"
                    f"score={subtotal}"
                )

        print()

        return score

    # ==========================================================

    @classmethod
    def classify(cls, document):

        text = cls.normalize(document.cleaned_markdown)

        print("\n" + "=" * 60)
        print("CLASSIFICATION")
        print("=" * 60)

        bank_score = cls.calculate_score(
            text,
            cls.BANK_KEYWORDS,
            "Bank Keyword Matches",
        )

        balance_score = cls.calculate_score(
            text,
            cls.BALANCE_KEYWORDS,
            "Balance Sheet Keyword Matches",
        )

        print(f"Bank Score          : {bank_score}")
        print(f"Balance Sheet Score : {balance_score}")
        print()

        if bank_score == 0 and balance_score == 0:

            return "unknown"

        if bank_score > balance_score:

            return "bank_statement"

        return "balance_sheet"
