import json
from pathlib import Path

from config import OUTPUT_DIR
from services.json_repair_service import JsonRepairService


class JsonRepairAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 60)
        print("JSON REPAIR")
        print("=" * 60)

        repaired_json = JsonRepairService.repair(document.llm_response)

        document.structured_data = repaired_json

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        repaired_folder = output_folder / "repaired"

        repaired_folder.mkdir(parents=True, exist_ok=True)

        repaired_file = repaired_folder / "repaired.json"

        with open(repaired_file, "w", encoding="utf-8") as file:

            json.dump(
                repaired_json,
                file,
                indent=4,
                ensure_ascii=False,
            )

        document.structured_data_path = str(repaired_file)

        print(f"Repaired JSON saved : {repaired_file}")

        return document
