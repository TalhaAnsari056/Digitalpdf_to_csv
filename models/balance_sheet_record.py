from dataclasses import dataclass


@dataclass
class BalanceSheetRecord:

    page: int

    section: str

    account_code: str

    account_name: str

    amount: float
