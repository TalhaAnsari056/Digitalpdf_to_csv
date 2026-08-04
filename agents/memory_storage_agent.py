from pathlib import Path

from services.memory_storage_service import MemoryStorageService


class MemoryStorageAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("MEMORY STORAGE")
        print("=" * 70)

        ############################################################
        # Orchestration only
        ############################################################

        document = MemoryStorageService.process(document)

        ############################################################
        # Terminal Summary
        ############################################################

        print("\nMemory Storage Summary")
        print("-" * 40)
        print(
            f"Memory File          : {Path(document.memory_path).name if document.memory_path else 'N/A'}"
        )
        print(
            f"Storage File         : {Path(document.memory_store_path).name if document.memory_store_path else 'N/A'}"
        )
        print(
            f"Storage Index        : {document.memory_index:06d}"
            if getattr(document, "memory_index", None) not in (None, "")
            else "Storage Index        : N/A"
        )
        print(
            f"Document ID          : {document.document_id if getattr(document, 'document_id', None) not in (None, '') else 'N/A'}"
        )

        print("\nMemory Storage completed successfully.")
        print("=" * 70)

        return document
