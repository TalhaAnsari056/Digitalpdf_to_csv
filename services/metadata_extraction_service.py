from __future__ import annotations

import json
from pathlib import Path

from config import OUTPUT_DIR
from services.llm_service import LLMService


class MetadataExtractionService:
    """
    Metadata Extraction Service.

    Business logic and LLM interaction for the new metadata stage.
    This stage only enriches the existing Document object.
    """

    REQUIRED_METADATA_FIELDS = [
        "company_name",
        "reporting_period",
        "statement_date",
        "document_type",
        "currency",
        "title",
        "fiscal_year",
    ]

    @staticmethod
    def process(document):

        if not document.cleaned_markdown:
            raise ValueError(
                "document.cleaned_markdown is required for metadata extraction."
            )

        ############################################################
        # Output folder
        ############################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "metadata"

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        metadata_prompt_file = output_folder / "metadata_prompt.txt"
        raw_response_file = output_folder / "raw_metadata_response.txt"
        metadata_file = output_folder / "metadata.json"
        report_file = output_folder / "extraction_report.json"

        ############################################################
        # Build prompt
        ############################################################

        prompt = MetadataExtractionService._build_prompt(document)

        # TODO: Prompt engineering will be added here later.
        # TODO: Add stricter JSON schema constraints and examples per document type.

        with open(metadata_prompt_file, "w", encoding="utf-8") as file:
            file.write(prompt)

        document.metadata_prompt = prompt
        document.metadata_prompt_path = str(metadata_prompt_file)

        ############################################################
        # Call LLM
        ############################################################

        llm_response = LLMService.generate(prompt)

        with open(raw_response_file, "w", encoding="utf-8") as file:
            file.write(llm_response)

        document.raw_metadata_response = llm_response
        document.raw_metadata_response_path = str(raw_response_file)

        ############################################################
        # Normalize output
        ############################################################

        metadata = MetadataExtractionService._normalize_metadata(llm_response)

        with open(metadata_file, "w", encoding="utf-8") as file:
            json.dump(
                metadata,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.metadata = metadata
        document.metadata_path = str(metadata_file)

        ############################################################
        # Save extraction report
        ############################################################

        report = {
            "document_type": document.document_type,
            "prompt_file": str(metadata_prompt_file),
            "raw_response_file": str(raw_response_file),
            "metadata_file": str(metadata_file),
            "metadata_fields": metadata,
        }

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.extraction_report = report
        document.extraction_report_path = str(report_file)

        return document

    @staticmethod
    def _build_prompt(document) -> str:

        document_type = (document.document_type or "").strip().lower()

        if document_type == "balance_sheet":
            return MetadataExtractionService._build_balance_sheet_prompt(
                document.cleaned_markdown
            )

        if document_type == "bank_statement":
            return MetadataExtractionService._build_bank_statement_prompt(
                document.cleaned_markdown
            )

        if document_type == "invoice":
            return MetadataExtractionService._build_invoice_prompt(
                document.cleaned_markdown
            )

        if document_type == "receipt":
            return MetadataExtractionService._build_receipt_prompt(
                document.cleaned_markdown
            )

        return MetadataExtractionService._build_generic_prompt(
            document.cleaned_markdown
        )

    @staticmethod
    def _build_balance_sheet_prompt(cleaned_markdown: str) -> str:

        prompt = f"""
You are extracting high-level document metadata from cleaned markdown content for a Balance Sheet.

Return valid JSON only.

Rules:
- Use only the cleaned markdown content.
- Do not modify or rewrite the markdown.
- Do not inspect CSV data.
- Do not inspect hierarchy.
- Do not hallucinate.
- If a field cannot be determined, return null.

Extract only these top-level fields:
- company_name
- reporting_period
- statement_date
- document_type
- currency
- title
- fiscal_year

Cleaned markdown:

{cleaned_markdown}
"""

        return prompt

    @staticmethod
    def _build_bank_statement_prompt(cleaned_markdown: str) -> str:

        # TODO: Add dedicated Bank Statement prompt engineering later.
        return MetadataExtractionService._build_generic_prompt(cleaned_markdown)

    @staticmethod
    def _build_invoice_prompt(cleaned_markdown: str) -> str:

        # TODO: Add dedicated Invoice prompt engineering later.
        return MetadataExtractionService._build_generic_prompt(cleaned_markdown)

    @staticmethod
    def _build_receipt_prompt(cleaned_markdown: str) -> str:

        # TODO: Add dedicated Receipt prompt engineering later.
        return MetadataExtractionService._build_generic_prompt(cleaned_markdown)

    @staticmethod
    def _build_generic_prompt(cleaned_markdown: str) -> str:

        prompt = f"""
You are extracting high-level document metadata from cleaned markdown content.

Return valid JSON only.

Rules:
- Use only the cleaned markdown content.
- Do not modify or rewrite the markdown.
- Do not inspect CSV data.
- Do not inspect hierarchy.
- Do not hallucinate.
- If a field cannot be determined, return null.

Extract only these top-level fields:
- company_name
- reporting_period
- statement_date
- document_type
- currency
- title
- fiscal_year

Cleaned markdown:

{cleaned_markdown}
"""

        return prompt

    @staticmethod
    def _normalize_metadata(llm_response: str) -> dict:

        normalized = {
            "company_name": None,
            "reporting_period": None,
            "statement_date": None,
            "document_type": None,
            "currency": None,
            "title": None,
            "fiscal_year": None,
        }

        ############################################################
        # Remove markdown code fences
        ############################################################

        cleaned = llm_response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "", 1)

        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "", 1)

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        ############################################################

        try:
            payload = json.loads(cleaned)

        except Exception as e:

            print("\nMetadata JSON Parse Error")
            print(e)

            payload = {}

        ############################################################

        for key in normalized:

            value = payload.get(key)

            if value in ("", "null", "None", "N/A", "n/a"):
                value = None

            normalized[key] = value

        return normalized

    # @staticmethod
    # def _normalize_metadata(llm_response: str) -> dict:

    #     normalized = {
    #         "company_name": None,
    #         "reporting_period": None,
    #         "statement_date": None,
    #         "document_type": None,
    #         "currency": None,
    #         "title": None,
    #         "fiscal_year": None,
    #     }

    #     try:
    #         payload = json.loads(llm_response)
    #     except Exception:
    #         payload = {}

    #     for key in normalized:
    #         value = payload.get(key)

    #         if value in (None, "", "null", "None", "N/A", "n/a"):
    #             normalized[key] = None
    #         else:
    #             normalized[key] = value

    #     return normalized
