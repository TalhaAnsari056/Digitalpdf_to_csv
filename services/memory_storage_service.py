from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from config import OUTPUT_DIR


class MemoryStorageService:
    """
    Memory Storage Service.

    Pure Python persistence layer for an already-generated document memory.
    This service does not call the LLM, does not perform embeddings, and does not use any vector database.
    It only stores the current document memory object into a persistent JSON array.
    """

    @staticmethod
    def process(document):

        if not getattr(document, "memory", None):
            raise ValueError("document.memory is required for memory storage.")

        storage_folder = OUTPUT_DIR / "memory_store"
        storage_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        storage_file = storage_folder / "memory_store.json"
        report_file = storage_folder / "memory_storage_report.json"

        if storage_file.exists():
            with open(storage_file, "r", encoding="utf-8") as file:
                try:
                    store = json.load(file)
                except json.JSONDecodeError:
                    store = []
        else:
            store = []

        if not isinstance(store, list):
            store = []

        metadata = getattr(document, "metadata", {}) or {}

        last_memory_id = 0
        if store:
            for entry in store:
                if isinstance(entry, dict):
                    current_id = entry.get("memory_id")
                    if isinstance(current_id, int) and current_id > last_memory_id:
                        last_memory_id = current_id

        memory_id = last_memory_id + 1
        document.memory_index = memory_id
        document.document_id = f"MEM-{memory_id:06d}"
        created_at = datetime.now(timezone.utc).isoformat()

        company = None
        if isinstance(metadata, dict):
            company = metadata.get("company_name") or metadata.get("company")

        statement_date = None
        if isinstance(metadata, dict):
            statement_date = metadata.get("statement_date")

        entry = {
            "memory_id": memory_id,
            "document_id": document.document_id,
            "created_at": created_at,
            "filename": getattr(document, "filename", None),
            "document_type": getattr(document, "document_type", None),
            "company": company,
            "statement_date": statement_date,
            "memory": document.memory,
        }

        store.append(entry)

        with open(storage_file, "w", encoding="utf-8") as file:
            json.dump(
                store,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.memory_store_path = str(storage_file)
        document.memory_store_entry = entry

        report = {
            "total_documents": len(store),
            "last_memory_id": memory_id,
            "last_company": company,
            "last_document_type": getattr(document, "document_type", None),
            "storage_path": str(storage_file),
        }

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.memory_store_report = report
        document.memory_store_report_path = str(report_file)

        return document
