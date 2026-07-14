from config import OUTPUT_DIR

from services.llm_service import LLMService


class LLMExtractionAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 60)
        print("LLM EXTRACTION")
        print("=" * 60)

        output_folder = OUTPUT_DIR / document.filename.replace(".pdf", "")

        prompt_path = output_folder / "prompt" / "prompt.txt"

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt = file.read()

        response = LLMService.generate(prompt)

        document.llm_response = response

        llm_folder = output_folder / "llm"

        llm_folder.mkdir(parents=True, exist_ok=True)

        raw_file = llm_folder / "raw_response.txt"

        with open(raw_file, "w", encoding="utf-8") as file:
            file.write(response)

        print("LLM response saved.")

        return document
