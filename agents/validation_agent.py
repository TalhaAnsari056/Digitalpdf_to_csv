import json
from dataclasses import fields

from config import OUTPUT_DIR


class ValidationAgent:

    @staticmethod
    def run(document):

        print("Validating Data...")

        report = []

        for index, record in enumerate(document.parsed_data):

            errors = []

            for field in fields(record):

                value = getattr(record, field.name)

                if value is None:

                    errors.append(f"{field.name} is None")

                elif isinstance(value, str):

                    if value.strip() == "":

                        errors.append(f"{field.name} is empty")

            report.append(
                {
                    "record": index + 1,
                    "errors": errors,
                }
            )

        validation_folder = (
            OUTPUT_DIR / document.filename.replace(".pdf", "") / "validated"
        )

        validation_folder.mkdir(parents=True, exist_ok=True)

        validation_file = validation_folder / "validation_report.json"

        with open(validation_file, "w", encoding="utf-8") as file:

            json.dump(report, file, indent=4)

        return document
