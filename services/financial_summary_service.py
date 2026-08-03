from __future__ import annotations

import json
from pathlib import Path

from config import OUTPUT_DIR
from services.llm_service import LLMService


class FinancialSummaryService:
    """
    Financial Summary Extraction Service.

    This stage consumes ONLY document.metadata and document.hierarchy.
    It does not inspect PDF, CSV, dataframe, or hierarchy internals beyond the given inputs.
    """

    REQUIRED_SUMMARY_FIELDS = [
        "company",
        "reporting_period",
        "statement_date",
        "currency",
        "document_type",
        "business_summary",
        "important_observations",
        "key_highlights",
        "warnings",
    ]

    @staticmethod
    def process(document):

        if not getattr(document, "metadata", None):
            raise ValueError(
                "document.metadata is required for financial summary extraction."
            )

        if not getattr(document, "hierarchy", None):
            raise ValueError(
                "document.hierarchy is required for financial summary extraction."
            )

        ############################################################
        # Output folder
        ############################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "financial_summary"

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        prompt_file = output_folder / "financial_summary_prompt.txt"
        raw_response_file = output_folder / "raw_financial_summary_response.txt"
        summary_file = output_folder / "financial_summary.json"
        report_file = output_folder / "financial_summary_report.json"

        ############################################################
        # Build prompt
        ############################################################

        prompt = FinancialSummaryService._build_prompt(document)

        with open(prompt_file, "w", encoding="utf-8") as file:
            file.write(prompt)

        document.financial_summary_prompt = prompt
        document.financial_summary_prompt_path = str(prompt_file)

        ############################################################
        # Call LLM
        ############################################################

        llm_response = LLMService.generate(prompt)

        with open(raw_response_file, "w", encoding="utf-8") as file:
            file.write(llm_response)

        document.raw_financial_summary_response = llm_response
        document.raw_financial_summary_response_path = str(raw_response_file)

        ############################################################
        # Normalize response
        ############################################################

        summary = FinancialSummaryService._normalize_summary(llm_response)

        with open(summary_file, "w", encoding="utf-8") as file:
            json.dump(
                summary,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.financial_summary = summary
        document.financial_summary_path = str(summary_file)

        ############################################################
        # Save report
        ############################################################

        report = {
            "document_type": getattr(document, "document_type", None),
            "prompt_file": str(prompt_file),
            "raw_response_file": str(raw_response_file),
            "summary_file": str(summary_file),
            "summary": summary,
        }

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.financial_summary_report = report
        document.financial_summary_report_path = str(report_file)

        return document

    @staticmethod
    def _build_prompt(document) -> str:

        document_type = (document.document_type or "").strip().lower()

        if document_type == "balance_sheet":
            return FinancialSummaryService._build_balance_sheet_prompt(
                document.metadata,
                document.hierarchy,
            )

        if document_type == "bank_statement":
            return FinancialSummaryService._build_bank_statement_prompt(
                document.metadata,
                document.hierarchy,
            )

        if document_type == "invoice":
            return FinancialSummaryService._build_invoice_prompt(
                document.metadata,
                document.hierarchy,
            )

        if document_type == "receipt":
            return FinancialSummaryService._build_receipt_prompt(
                document.metadata,
                document.hierarchy,
            )

        return FinancialSummaryService._build_generic_prompt(
            document.metadata,
            document.hierarchy,
        )

    @staticmethod
    def _build_balance_sheet_prompt(metadata: dict, hierarchy: dict) -> str:

        metadata_context = json.dumps(metadata, indent=4, ensure_ascii=False)
        hierarchy_context = json.dumps(hierarchy, indent=4, ensure_ascii=False)

        prompt = (
            "You are producing a concise business summary from validated document metadata and hierarchy only.\n\n"
            "Return ONLY valid JSON.\n\n"
            "Rules:\n"
            "- Read ONLY document.metadata and document.hierarchy.\n"
            "- Never reproduce the hierarchy itself.\n"
            "- Never reproduce account tables.\n"
            "- Never reproduce Assets/Liabilities/Equity JSON.\n"
            "- Never calculate totals.\n"
            "- Never calculate ratios.\n"
            "- Never invent values.\n"
            "- If information is unavailable, use null.\n"
            "- Output only a short business understanding of the balance sheet.\n"
            "- Output JSON only, with no markdown, no explanations, and no code fences.\n\n"
            "Required JSON keys:\n"
            "- company\n"
            "- reporting_period\n"
            "- statement_date\n"
            "- currency\n"
            "- document_type\n"
            "- business_summary\n"
            "- important_observations\n"
            "- key_highlights\n"
            "- warnings\n\n"
            f"Metadata context:\n{metadata_context}\n\n"
            f"Hierarchy context:\n{hierarchy_context}\n"
        )

        return prompt

    @staticmethod
    def _build_bank_statement_prompt(metadata: dict, hierarchy: dict) -> str:

        # TODO: Implement Bank Statement prompt engineering later.
        return FinancialSummaryService._build_generic_prompt(metadata, hierarchy)

    @staticmethod
    def _build_invoice_prompt(metadata: dict, hierarchy: dict) -> str:

        # TODO: Implement Invoice prompt engineering later.
        return FinancialSummaryService._build_generic_prompt(metadata, hierarchy)

    @staticmethod
    def _build_receipt_prompt(metadata: dict, hierarchy: dict) -> str:

        # TODO: Implement Receipt prompt engineering later.
        return FinancialSummaryService._build_generic_prompt(metadata, hierarchy)

    @staticmethod
    def _build_generic_prompt(metadata: dict, hierarchy: dict) -> str:

        metadata_context = json.dumps(metadata, indent=4, ensure_ascii=False)
        hierarchy_context = json.dumps(hierarchy, indent=4, ensure_ascii=False)

        prompt = (
            "You are producing a canonical business summary from validated, already-extracted document metadata and hierarchy.\n\n"
            "Return ONLY valid JSON.\n\n"
            "Rules:\n"
            "- Consume ONLY document.metadata and document.hierarchy.\n"
            "- Do not inspect PDF, CSV, dataframe, or raw extraction output.\n"
            "- Do not hallucinate.\n"
            "- Use null whenever information cannot be determined.\n"
            "- Do not perform unsupported calculations.\n"
            "- Only summarize existing validated information.\n"
            "- Output JSON only, with no markdown, no explanations, and no code fences.\n\n"
            f"Metadata context:\n{metadata_context}\n\n"
            f"Hierarchy context:\n{hierarchy_context}\n"
        )

        return prompt

    @staticmethod
    def _normalize_summary(llm_response: str) -> dict:

        if llm_response is None:
            raise ValueError("Financial summary response is empty.")

        cleaned_response = llm_response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.strip("`")

            if cleaned_response.lower().startswith("json"):
                cleaned_response = cleaned_response[4:].strip()

        try:
            payload = json.loads(cleaned_response)
        except Exception as exc:
            raise ValueError(
                f"Financial summary response is not valid JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError("Financial summary response must be a JSON object.")

        normalized = {
            "company": None,
            "reporting_period": None,
            "statement_date": None,
            "currency": None,
            "document_type": None,
            "business_summary": None,
            "important_observations": None,
            "key_highlights": None,
            "warnings": None,
        }

        for key in normalized:
            value = payload.get(key)

            if value in (None, "", "null", "None", "N/A", "n/a"):
                normalized[key] = None
            else:
                normalized[key] = value

        return normalized
