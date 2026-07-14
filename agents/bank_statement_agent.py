from pathlib import Path

from config import OUTPUT_DIR
from services.prompt_builder_service import PromptBuilderService


class BankStatementAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 60)
        print("BANK STATEMENT AGENT")
        print("=" * 60)

        # ----------------------------------------
        # Build Prompt
        # ----------------------------------------

        prompt = PromptBuilderService.build(document)

        document.prompt = prompt

        # ----------------------------------------
        # Save Prompt
        # ----------------------------------------

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        prompt_folder = output_folder / "prompt"

        prompt_folder.mkdir(parents=True, exist_ok=True)

        prompt_file = prompt_folder / "prompt.txt"

        with open(prompt_file, "w", encoding="utf-8") as file:
            file.write(prompt)

        document.prompt_path = str(prompt_file)

        print(f"Prompt saved : {prompt_file}")

        return document
