from __future__ import annotations

import json
from pathlib import Path

from config import OUTPUT_DIR
from services.llm_service import LLMService


class MemoryService:
    """
    Memory Service.

    This stage converts Financial Summary + Financial Analytics into compact long-term memory.
    It consumes only document.financial_summary and document.financial_analytics.
    It must not inspect metadata, markdown, hierarchy, CSV, dataframe, or raw extraction outputs.
    """

    REQUIRED_MEMORY_FIELDS = [
        "memory_summary",
        "long_term_facts",
        "decision_rationale",
    ]

    @staticmethod
    def process(document):

        if not getattr(document, "financial_summary", None):
            raise ValueError(
                "document.financial_summary is required for memory generation."
            )

        if not getattr(document, "financial_analytics", None):
            raise ValueError(
                "document.financial_analytics is required for memory generation."
            )

        ############################################################
        # Output folder
        ############################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem / "memory"

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        prompt_file = output_folder / "memory_prompt.txt"
        raw_response_file = output_folder / "raw_memory_response.txt"
        memory_file = output_folder / "memory.json"
        report_file = output_folder / "memory_report.json"

        ############################################################
        # Build prompt
        ############################################################

        prompt = MemoryService._build_prompt(document)

        # TODO: Prompt engineering will be added later.
        # TODO: Add stricter schema and retention heuristics once the long-term memory contract is finalized.

        with open(prompt_file, "w", encoding="utf-8") as file:
            file.write(prompt)

        document.memory_prompt = prompt
        document.memory_prompt_path = str(prompt_file)

        ############################################################
        # Call LLM
        ############################################################

        llm_response = LLMService.generate(prompt)

        with open(raw_response_file, "w", encoding="utf-8") as file:
            file.write(llm_response)

        document.raw_memory_response = llm_response
        document.raw_memory_response_path = str(raw_response_file)

        ############################################################
        # Normalize response
        ############################################################

        memory = MemoryService._normalize_memory(llm_response)

        with open(memory_file, "w", encoding="utf-8") as file:
            json.dump(
                memory,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.memory = memory
        document.memory_path = str(memory_file)

        ############################################################
        # Save report
        ############################################################

        report = {
            "document_type": getattr(document, "document_type", None),
            "prompt_file": str(prompt_file),
            "raw_response_file": str(raw_response_file),
            "memory_file": str(memory_file),
            "memory": memory,
        }

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.memory_report = report
        document.memory_report_path = str(report_file)

        return document

    @staticmethod
    def _build_prompt(document) -> str:

        summary_context = json.dumps(
            document.financial_summary,
            indent=4,
            ensure_ascii=False,
        )
        analytics_context = json.dumps(
            document.financial_analytics,
            indent=4,
            ensure_ascii=False,
        )

        prompt = (
            "This stage converts Financial Summary + Financial Analytics into compact long-term memory.\n\n"
            "Your job is not to re-extract, re-summarize, or recalculate anything.\n"
            "Your job is to decide which durable business facts are valuable enough to remember later.\n\n"
            "Return ONLY valid JSON in exactly this shape:\n"
            "{\n"
            '  "memory_summary": "...",\n'
            '  "long_term_facts": [\n'
            "    ...\n"
            "  ],\n"
            '  "decision_rationale": "..."\n'
            "}\n\n"
            "Rules:\n"
            "- Consume ONLY document.financial_summary and document.financial_analytics.\n"
            "- Do NOT summarize the document again.\n"
            "- Do NOT restate every value.\n"
            "- Do NOT recreate financial_summary.\n"
            "- Do NOT calculate anything.\n"
            "- Do NOT extract information.\n"
            "- Do NOT inspect metadata, markdown, hierarchy, CSV, dataframe, parser output, validator output, or raw extraction output.\n"
            "- Identify only durable business knowledge that should survive for future reasoning.\n"
            "- memory_summary should be 2-4 sentences that another AI agent could quickly read months later.\n"
            "- long_term_facts should contain only the facts worth remembering later, such as company identity, document type, major financial position, unusually large accounts, major risks, negative equity items, and important observations.\n"
            "- Do not include every account. Keep the list compact and selective.\n"
            "- decision_rationale should briefly explain why these facts were selected for long-term memory.\n"
            "- Use null whenever information cannot be determined.\n"
            "- Output JSON only, with no markdown, no explanations, and no code fences.\n\n"
            "TODO: Prompt engineering will be added later once the long-term memory selection contract is finalized.\n\n"
            f"Financial summary context:\n{summary_context}\n\n"
            f"Financial analytics context:\n{analytics_context}\n"
        )

        return prompt

    @staticmethod
    def _normalize_memory(llm_response: str) -> dict:

        if llm_response is None:
            raise ValueError("Memory response is empty.")

        cleaned_response = llm_response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.strip("`")

            if cleaned_response.lower().startswith("json"):
                cleaned_response = cleaned_response[4:].strip()

        try:
            payload = json.loads(cleaned_response)
        except Exception as exc:
            raise ValueError(f"Memory response is not valid JSON: {exc}") from exc

        if not isinstance(payload, dict):
            raise ValueError("Memory response must be a JSON object.")

        normalized = {
            "memory_summary": None,
            "long_term_facts": None,
            "decision_rationale": None,
        }

        for key in normalized:
            value = payload.get(key)

            if value in (None, "", "null", "None", "N/A", "n/a"):
                normalized[key] = None
            else:
                normalized[key] = value

        return normalized
