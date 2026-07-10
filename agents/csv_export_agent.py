import csv
from dataclasses import asdict

from config import OUTPUT_DIR


class CSVExportAgent:

    @staticmethod
    def run(document):

        print("Exporting CSV...")

        if not document.parsed_data:

            print("Nothing to export.")

            return

        csv_folder = OUTPUT_DIR / document.filename.replace(".pdf", "") / "csv"

        csv_folder.mkdir(parents=True, exist_ok=True)

        csv_file = csv_folder / "output.csv"

        rows = [asdict(record) for record in document.parsed_data]

        headers = rows[0].keys()

        with open(csv_file, "w", newline="", encoding="utf-8") as file:

            writer = csv.DictWriter(file, fieldnames=headers)

            writer.writeheader()

            writer.writerows(rows)

        print(f"CSV Saved : {csv_file}")
