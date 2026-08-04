from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import OUTPUT_DIR


class CompanyMemoryBuilderService:
    """
    Company Memory Builder Service.

    Pure deterministic aggregation layer.
    This service reads the persisted memory store and builds one consolidated company memory profile per company.
    It does not call any LLM, does not perform embeddings, and does not use any vector database.
    """

    @staticmethod
    def process():

        storage_file = OUTPUT_DIR / "memory_store" / "memory_store.json"

        if not storage_file.exists():
            raise FileNotFoundError(
                "Memory store does not exist. Run MemoryStorageService first."
            )

        with open(storage_file, "r", encoding="utf-8") as file:
            memory_store = json.load(file)

        if not isinstance(memory_store, list):
            raise ValueError("Memory store must contain a JSON array.")

        company_profiles = CompanyMemoryBuilderService._build_company_profiles(
            memory_store
        )

        output_folder = OUTPUT_DIR / "company_memory"
        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        company_memory_file = output_folder / "company_memory.json"
        company_report_file = output_folder / "company_memory_report.json"

        with open(company_memory_file, "w", encoding="utf-8") as file:
            json.dump(
                company_profiles,
                file,
                indent=4,
                ensure_ascii=False,
            )

        timestamp = datetime.now(timezone.utc).isoformat()

        report = {
            "total_companies": len(company_profiles),
            "total_documents_processed": len(memory_store),
            "companies_updated": len(company_profiles),
            "output_path": str(company_memory_file),
            "timestamp": timestamp,
        }

        with open(company_report_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return company_profiles

    @staticmethod
    def _build_company_profiles(
        memory_store: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        grouped_docs: dict[str, list[dict[str, Any]]] = {}

        for entry in memory_store:
            if not isinstance(entry, dict):
                continue

            company_name = entry.get("company")

            if not company_name:
                continue

            grouped_docs.setdefault(str(company_name), []).append(entry)

        company_profiles: list[dict[str, Any]] = []
        company_index = 1

        for company_name in sorted(grouped_docs.keys()):
            documents = grouped_docs[company_name]

            document_ids = []
            document_types = []
            statement_dates = []
            memory_summaries = []
            long_term_facts = []
            known_risks = []
            decision_history = []

            for document in documents:
                memory = document.get("memory") or {}

                document_id = document.get("memory_id")
                if document_id is not None:
                    document_ids.append(document_id)

                document_type = document.get("document_type")
                if document_type:
                    document_types.append(document_type)

                statement_date = document.get("statement_date")
                if statement_date:
                    statement_dates.append(statement_date)

                memory_summary = memory.get("memory_summary")
                if memory_summary:
                    memory_summaries.append(memory_summary)

                facts = memory.get("long_term_facts") or []
                if isinstance(facts, list):
                    for fact in facts:
                        if fact not in long_term_facts:
                            long_term_facts.append(fact)

                rationale = memory.get("decision_rationale")
                if rationale:
                    decision_history.append(rationale)

                if isinstance(memory, dict):
                    risks = memory.get("known_risks") or []
                    if isinstance(risks, list):
                        for risk in risks:
                            if risk not in known_risks:
                                known_risks.append(risk)

            document_ids = CompanyMemoryBuilderService._sorted_ids(document_ids)
            document_types = CompanyMemoryBuilderService._deduplicate(document_types)
            statement_dates = CompanyMemoryBuilderService._sort_dates(statement_dates)
            memory_summaries = CompanyMemoryBuilderService._preserve_order(
                memory_summaries
            )
            long_term_facts = CompanyMemoryBuilderService._preserve_order(
                long_term_facts
            )
            decision_history = CompanyMemoryBuilderService._preserve_order(
                decision_history
            )
            known_risks = CompanyMemoryBuilderService._preserve_order(known_risks)

            created_at = documents[0].get("created_at") if documents else None
            updated_at = documents[-1].get("created_at") if documents else None

            company_profiles.append(
                {
                    "company_id": f"COMP-{company_index:06d}",
                    "company_name": company_name,
                    "documents_seen": len(documents),
                    "document_ids": document_ids,
                    "document_types": document_types,
                    "statement_dates": statement_dates,
                    "memory_summaries": memory_summaries,
                    "long_term_facts": long_term_facts,
                    "known_risks": known_risks,
                    "decision_history": decision_history,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
            )

            company_index += 1

        return company_profiles

    @staticmethod
    def _deduplicate(values: list[Any]) -> list[Any]:
        seen = set()
        ordered: list[Any] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                ordered.append(value)
        return ordered

    @staticmethod
    def _preserve_order(values: list[Any]) -> list[Any]:
        return values

    @staticmethod
    def _sorted_ids(values: list[Any]) -> list[Any]:
        return sorted(values)

    @staticmethod
    def _sort_dates(values: list[Any]) -> list[Any]:

        sortable = []
        for value in values:
            if not value:
                continue
            try:
                sortable.append((value, datetime.fromisoformat(str(value))))
            except Exception:
                sortable.append((value, None))

        sortable.sort(key=lambda item: (item[1] is None, item[1] or datetime.min))

        return [value for value, _ in sortable]
