from dataclasses import dataclass


@dataclass
class BankStatementRecord:

    page: int

    date: str

    description: str

    debit: float | None

    credit: float | None

    balance: float | None

    currency: str = ""
