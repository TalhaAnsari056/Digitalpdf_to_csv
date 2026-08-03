from __future__ import annotations

import json
from pathlib import Path

from config import OUTPUT_DIR
from services.llm_service import LLMService


class HierarchyExtractionService:
    """
    Hierarchy Extraction Service.

    Business logic and LLM interaction for the new hierarchy stage.
    This stage only enriches the existing Document object.
    """

    @staticmethod
    def process(document):

        if not document.validated_markdown:
            raise ValueError(
                "document.validated_markdown is required for hierarchy extraction."
            )

        if not getattr(document, "metadata", None):
            raise ValueError("document.metadata is required for hierarchy extraction.")

        ############################################################
        # Output folder
        ############################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "hierarchy"

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        hierarchy_prompt_file = output_folder / "hierarchy_prompt.txt"
        raw_response_file = output_folder / "raw_hierarchy_response.txt"
        hierarchy_file = output_folder / "hierarchy.json"
        report_file = output_folder / "extraction_report.json"

        ############################################################
        # Build prompt
        ############################################################

        prompt = HierarchyExtractionService._build_prompt(document)

        # TODO: Add prompt engineering for Bank Statement, Invoice, and Receipt later.

        with open(hierarchy_prompt_file, "w", encoding="utf-8") as file:
            file.write(prompt)

        document.hierarchy_prompt = prompt
        document.hierarchy_prompt_path = str(hierarchy_prompt_file)

        ############################################################
        # Call LLM
        ############################################################

        llm_response = LLMService.generate(prompt)

        with open(raw_response_file, "w", encoding="utf-8") as file:
            file.write(llm_response)

        document.raw_hierarchy_response = llm_response
        document.raw_hierarchy_response_path = str(raw_response_file)

        ############################################################
        # Normalize output
        ############################################################

        hierarchy = HierarchyExtractionService._normalize_hierarchy(llm_response)

        with open(hierarchy_file, "w", encoding="utf-8") as file:
            json.dump(
                hierarchy,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.hierarchy = hierarchy
        document.hierarchy_path = str(hierarchy_file)

        ############################################################
        # Save extraction report
        ############################################################

        report = {
            "document_type": getattr(document, "document_type", None),
            "prompt_file": str(hierarchy_prompt_file),
            "raw_response_file": str(raw_response_file),
            "hierarchy_file": str(hierarchy_file),
            "hierarchy": hierarchy,
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
            return HierarchyExtractionService._build_balance_sheet_prompt(
                document.validated_markdown,
                document.metadata,
            )

        if document_type == "bank_statement":
            return HierarchyExtractionService._build_bank_statement_prompt(
                document.validated_markdown,
                document.metadata,
            )

        if document_type == "invoice":
            return HierarchyExtractionService._build_invoice_prompt(
                document.validated_markdown,
                document.metadata,
            )

        if document_type == "receipt":
            return HierarchyExtractionService._build_receipt_prompt(
                document.validated_markdown,
                document.metadata,
            )

        return HierarchyExtractionService._build_generic_prompt(
            document.validated_markdown,
            document.metadata,
        )

    @staticmethod
    def _build_balance_sheet_prompt(validated_markdown: str, metadata: dict) -> str:

        metadata_context = json.dumps(metadata, indent=4, ensure_ascii=False)

        prompt = (
            "You are preserving the logical hierarchy of a balance sheet before it is flattened into tabular form.\n\n"
            "Return ONLY valid JSON.\n\n"
            "Rules:\n"
            "- Read document.validated_markdown and the supplied metadata.\n"
            "- Preserve the original hierarchy structure.\n"
            "- Do not flatten accounts into one level.\n"
            "- Do not remove any account.\n"
            "- Every account must remain under its correct parent section.\n"
            "- Do not inspect CSV files.\n"
            "- Do not inspect normalized dataframe.\n"
            "- Do not hallucinate.\n"
            "- If an account or section cannot be determined, return null.\n"
            "- Output JSON only.\n\n"
            "Required hierarchy structure:\n\n"
            "{\n"
            '  "Assets": {\n'
            '    "Current Assets": {\n'
            '      "Accounts": [\n'
            "        {\n"
            '          "account_name": "...",\n'
            '          "amount": "..."\n'
            "        }\n"
            "      ]\n"
            "    },\n"
            '    "Non Current Assets": {\n'
            '      "Accounts": [\n'
            "        {\n"
            '          "account_name": "...",\n'
            '          "amount": "..."\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  },\n"
            '  "Liabilities": {\n'
            '    "Current Liabilities": {\n'
            '      "Accounts": [\n'
            "        {\n"
            '          "account_name": "...",\n'
            '          "amount": "..."\n'
            "        }\n"
            "      ]\n"
            "    },\n"
            '    "Non Current Liabilities": {\n'
            '      "Accounts": [\n'
            "        {\n"
            '          "account_name": "...",\n'
            '          "amount": "..."\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  },\n"
            '  "Equity": {\n'
            '    "Accounts": [\n'
            "      {\n"
            '        "account_name": "...",\n'
            '        "amount": "..."\n'
            "      }\n"
            "    ]\n"
            "  }\n"
            "}\n\n"
            f"Metadata context:\n{metadata_context}\n\n"
            "Validated markdown:\n\n"
            f"{validated_markdown}\n"
        )

        return prompt

    @staticmethod
    def _build_bank_statement_prompt(validated_markdown: str, metadata: dict) -> str:

        # TODO: Implement Bank Statement hierarchy prompt later.
        return HierarchyExtractionService._build_generic_prompt(
            validated_markdown,
            metadata,
        )

    @staticmethod
    def _build_invoice_prompt(validated_markdown: str, metadata: dict) -> str:

        # TODO: Implement Invoice hierarchy prompt later.
        return HierarchyExtractionService._build_generic_prompt(
            validated_markdown,
            metadata,
        )

    @staticmethod
    def _build_receipt_prompt(validated_markdown: str, metadata: dict) -> str:

        # TODO: Implement Receipt hierarchy prompt later.
        return HierarchyExtractionService._build_generic_prompt(
            validated_markdown,
            metadata,
        )

    @staticmethod
    def _build_generic_prompt(validated_markdown: str, metadata: dict) -> str:

        metadata_context = json.dumps(metadata, indent=4, ensure_ascii=False)

        prompt = f"""
You are extracting a document hierarchy while preserving the original logical structure.

Return ONLY valid JSON.

Rules:
- Read document.validated_markdown and the supplied metadata.
- Preserve logical grouping and parent-child structure.
- Preserve the original section order.
- Preserve the original row order within each section.
- Preserve subtotal rows in-place and do not drop them.
- Do not flatten the hierarchy.
- Do not inspect CSV files.
- Do not inspect normalized dataframe.
- Do not hallucinate.
- If a field cannot be determined, return null.

Metadata context:
{metadata_context}

Validated markdown:

{validated_markdown}
"""

        return prompt

    @staticmethod
    def _normalize_hierarchy(llm_response: str) -> dict:

        if llm_response is None:
            raise ValueError("Hierarchy response is empty.")

        cleaned_response = llm_response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.strip("`")

            if cleaned_response.lower().startswith("json"):
                cleaned_response = cleaned_response[4:].strip()

        try:
            payload = json.loads(cleaned_response)
        except Exception as exc:
            raise ValueError(f"Hierarchy response is not valid JSON: {exc}") from exc

        if not isinstance(payload, dict):
            raise ValueError("Hierarchy response must be a JSON object.")

        return payload
