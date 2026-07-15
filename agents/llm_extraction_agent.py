# from config import OUTPUT_DIR

# from services.llm_service import LLMService


# class LLMExtractionAgent:

#     @staticmethod
#     def run(document):

#         print("\n" + "=" * 60)
#         print("LLM EXTRACTION")
#         print("=" * 60)

#         output_folder = OUTPUT_DIR / document.filename.replace(".pdf", "")

#         prompt_path = output_folder / "prompt" / "prompt.txt"

#         with open(prompt_path, "r", encoding="utf-8") as file:
#             prompt = file.read()

#         response = LLMService.generate(prompt)

#         document.llm_response = response

#         llm_folder = output_folder / "llm"

#         llm_folder.mkdir(parents=True, exist_ok=True)

#         raw_file = llm_folder / "raw_response.txt"

#         with open(raw_file, "w", encoding="utf-8") as file:
#             file.write(response)

#         print("LLM response saved.")

#         return document
from pathlib import Path

from config import OUTPUT_DIR

from services.prompt_builder_service import PromptBuilderService
from services.llm_service import LLMService


class LLMExtractionAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 60)
        print("LLM EXTRACTION")
        print("=" * 60)

        ####################################################
        # Build Prompt
        ####################################################

        prompt = PromptBuilderService.build(document)

        document.prompt = prompt

        ####################################################
        # Output Folder
        ####################################################

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        ####################################################
        # Save Prompt
        ####################################################

        prompt_folder = output_folder / "prompt"

        prompt_folder.mkdir(parents=True, exist_ok=True)

        prompt_file = prompt_folder / "prompt.txt"

        with open(prompt_file, "w", encoding="utf-8") as file:
            file.write(prompt)

        ####################################################
        # Call LLM
        ####################################################

        mapped_markdown = LLMService.generate(prompt)

        document.llm_response = mapped_markdown

        ####################################################
        # Save Mapped Markdown
        ####################################################

        llm_folder = output_folder / "llm"

        llm_folder.mkdir(parents=True, exist_ok=True)

        markdown_file = llm_folder / "mapped_markdown.md"

        with open(markdown_file, "w", encoding="utf-8") as file:
            file.write(mapped_markdown)

        print(f"Mapped markdown saved : {markdown_file}")

        return document
