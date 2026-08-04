from pathlib import Path

from services.memory_service import MemoryService


class MemoryAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("MEMORY AGENT")
        print("=" * 70)

        ############################################################
        # Orchestration only
        ############################################################

        document = MemoryService.process(document)

        ############################################################
        # Terminal Summary
        ############################################################

        print("\nMemory Summary")
        print("-" * 40)
        print(f"Document              : {document.filename}")
        print(
            f"Prompt File            : {Path(document.memory_prompt_path).name if document.memory_prompt_path else 'N/A'}"
        )
        print(
            f"Raw Response File      : {Path(document.raw_memory_response_path).name if document.raw_memory_response_path else 'N/A'}"
        )
        print(
            f"Memory File            : {Path(document.memory_path).name if document.memory_path else 'N/A'}"
        )
        print(
            f"Memory Report File     : {Path(document.memory_report_path).name if document.memory_report_path else 'N/A'}"
        )

        print("\nMemory Agent completed successfully.")
        print("=" * 70)

        return document
