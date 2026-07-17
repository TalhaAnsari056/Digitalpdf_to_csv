from pathlib import Path

from config import OUTPUT_DIR


class CSVExportAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 60)
        print("CSV EXPORT")
        print("=" * 60)

        if document.dataframe is None:

            print("No dataframe available.")

            return document

        output_folder = OUTPUT_DIR / Path(document.filename).stem

        csv_folder = output_folder / "csv"

        csv_folder.mkdir(parents=True, exist_ok=True)

        csv_file = csv_folder / "output.csv"

        document.dataframe.to_csv(
            csv_file,
            index=False,
            encoding="utf-8",
        )

        document.csv_path = str(csv_file)

        print(f"CSV saved : {csv_file}")

        return document
