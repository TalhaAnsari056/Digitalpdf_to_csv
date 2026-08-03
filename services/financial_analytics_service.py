from __future__ import annotations

import json
from pathlib import Path

from config import OUTPUT_DIR


class FinancialAnalyticsService:
    """
    Financial Analytics Service.

    Deterministic business calculations only.
    This stage consumes document.hierarchy and derives analytics directly from the hierarchy tree.
    It must not call any LLM.
    """

    @staticmethod
    def process(document):

        if not getattr(document, "hierarchy", None):
            raise ValueError("document.hierarchy is required for financial analytics.")

        ############################################################
        # Output folder
        ############################################################

        output_folder = (
            OUTPUT_DIR / Path(document.filename).stem / "financial_analytics"
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        analytics_file = output_folder / "financial_analytics.json"
        report_file = output_folder / "financial_analytics_report.json"

        ############################################################
        # Compute analytics
        ############################################################

        analytics = FinancialAnalyticsService._compute_analytics(document)

        ############################################################
        # Save analytics
        ############################################################

        with open(analytics_file, "w", encoding="utf-8") as file:
            json.dump(
                analytics,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.financial_analytics = analytics
        document.financial_analytics_path = str(analytics_file)

        ############################################################
        # Save report
        ############################################################

        report = {
            "document_type": getattr(document, "document_type", None),
            "analytics_file": str(analytics_file),
            "analytics": analytics,
        }

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.financial_analytics_report = report
        document.financial_analytics_report_path = str(report_file)

        return document

    @staticmethod
    def _compute_analytics(document):

        hierarchy = document.hierarchy or {}

        current_assets_accounts = FinancialAnalyticsService._get_accounts(
            hierarchy,
            ["Assets", "Current Assets"],
        )
        non_current_assets_accounts = FinancialAnalyticsService._get_accounts(
            hierarchy,
            ["Assets", "Non Current Assets"],
        )
        current_liabilities_accounts = FinancialAnalyticsService._get_accounts(
            hierarchy,
            ["Liabilities", "Current Liabilities"],
        )
        non_current_liabilities_accounts = FinancialAnalyticsService._get_accounts(
            hierarchy,
            ["Liabilities", "Non Current Liabilities"],
        )
        equity_accounts = FinancialAnalyticsService._get_accounts(
            hierarchy,
            ["Equity"],
        )

        current_assets_total = FinancialAnalyticsService._extract_total(
            current_assets_accounts
        )
        non_current_assets_total = FinancialAnalyticsService._extract_total(
            non_current_assets_accounts
        )
        current_liabilities_total = FinancialAnalyticsService._extract_total(
            current_liabilities_accounts
        )
        non_current_liabilities_total = FinancialAnalyticsService._extract_total(
            non_current_liabilities_accounts
        )
        total_equity = FinancialAnalyticsService._extract_total(equity_accounts)

        total_assets = None
        if current_assets_total is not None and non_current_assets_total is not None:
            total_assets = current_assets_total + non_current_assets_total

        total_liabilities = None
        if (
            current_liabilities_total is not None
            and non_current_liabilities_total is not None
        ):
            total_liabilities = (
                current_liabilities_total + non_current_liabilities_total
            )

        working_capital = None
        if current_assets_total is not None and current_liabilities_total is not None:
            working_capital = current_assets_total - current_liabilities_total

        asset_to_liability_ratio = None
        if total_assets not in (None, 0) and total_liabilities is not None:
            asset_to_liability_ratio = total_assets / total_liabilities

        equity_ratio = None
        if total_assets not in (None, 0) and total_equity is not None:
            equity_ratio = total_equity / total_assets

        largest_asset_account = FinancialAnalyticsService._find_largest_account(
            current_assets_accounts + non_current_assets_accounts
        )
        largest_liability_account = FinancialAnalyticsService._find_largest_account(
            current_liabilities_accounts + non_current_liabilities_accounts
        )
        largest_equity_account = FinancialAnalyticsService._find_largest_account(
            equity_accounts
        )

        all_accounts = (
            current_assets_accounts
            + non_current_assets_accounts
            + current_liabilities_accounts
            + non_current_liabilities_accounts
            + equity_accounts
        )

        negative_accounts = FinancialAnalyticsService._find_negative_accounts(
            all_accounts
        )

        number_of_accounts = FinancialAnalyticsService._count_accounts(all_accounts)

        balance_sheet_balanced = None
        if (
            total_assets is not None
            and total_liabilities is not None
            and total_equity is not None
        ):
            difference = abs(total_assets - (total_liabilities + total_equity))
            balance_sheet_balanced = difference <= 1.0

        analytics = {
            "working_capital": working_capital,
            "asset_to_liability_ratio": asset_to_liability_ratio,
            "equity_ratio": equity_ratio,
            "largest_asset_account": largest_asset_account,
            "largest_liability_account": largest_liability_account,
            "largest_equity_account": largest_equity_account,
            "negative_accounts": negative_accounts,
            "number_of_accounts": number_of_accounts,
            "current_assets_total": current_assets_total,
            "current_liabilities_total": current_liabilities_total,
            "non_current_assets_total": non_current_assets_total,
            "non_current_liabilities_total": non_current_liabilities_total,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "balance_sheet_balanced": balance_sheet_balanced,
        }

        return analytics

    @staticmethod
    def _get_accounts(node, path):

        current = node

        for key in path:
            if not isinstance(current, dict):
                return []

            current = current.get(key)

            if current is None:
                return []

        if not isinstance(current, dict):
            return []

        accounts = current.get("Accounts")

        if not isinstance(accounts, list):
            return []

        parsed_accounts = []

        for entry in accounts:
            if not isinstance(entry, dict):
                continue

            parsed_accounts.append(
                {
                    "account_name": entry.get("account_name"),
                    "amount": FinancialAnalyticsService._parse_amount(
                        entry.get("amount")
                    ),
                }
            )

        return parsed_accounts

    @staticmethod
    def _extract_total(accounts):

        if not accounts:
            return None

        last_entry = accounts[-1]
        if not isinstance(last_entry, dict):
            return None

        return FinancialAnalyticsService._parse_amount(last_entry.get("amount"))

    @staticmethod
    def _find_largest_account(accounts):

        if not accounts:
            return None

        real_accounts = []

        for account in accounts:
            if FinancialAnalyticsService._is_summary_account(account):
                continue

            amount = account.get("amount")
            if amount is None:
                continue

            real_accounts.append(account)

        if not real_accounts:
            return None

        return max(
            real_accounts,
            key=lambda item: abs(item.get("amount", 0)),
        )

    @staticmethod
    def _find_negative_accounts(accounts):

        negative_accounts = []

        for account in accounts:
            if FinancialAnalyticsService._is_summary_account(account):
                continue

            amount = account.get("amount")
            if amount is None:
                continue

            if amount < 0:
                negative_accounts.append(
                    {
                        "account_name": account.get("account_name"),
                        "amount": amount,
                    }
                )

        return negative_accounts

    @staticmethod
    def _count_accounts(accounts):

        if not accounts:
            return 0

        count = 0

        for account in accounts:
            if FinancialAnalyticsService._is_summary_account(account):
                continue

            if account.get("amount") is None:
                continue

            count += 1

        return count

    @staticmethod
    def _is_summary_account(account):

        if not isinstance(account, dict):
            return True

        account_name = str(account.get("account_name") or "").strip().lower()
        return "total" in account_name or "subtotal" in account_name

    @staticmethod
    def _parse_amount(value):

        if value in (None, "", "null", "None", "N/A", "n/a"):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned == "":
                return None

            cleaned = cleaned.replace(",", "")
            cleaned = cleaned.replace("(", "-").replace(")", "")

            try:
                return float(cleaned)
            except Exception:
                return None

        return None
