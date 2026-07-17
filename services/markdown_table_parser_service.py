import io
import pandas as pd


class MarkdownTableParserService:

    @staticmethod
    def parse(markdown: str) -> pd.DataFrame:

        markdown = markdown.strip()

        if not markdown:
            raise ValueError("Empty markdown received.")

        lines = []

        for line in markdown.splitlines():

            line = line.strip()

            if not line:
                continue

            if not line.startswith("|"):
                continue

            # Skip separator row
            if (
                set(line.replace("|", "").replace("-", "").replace(":", "").strip())
                == set()
            ):
                continue

            lines.append(line)

        if len(lines) < 2:
            raise ValueError("No markdown table found.")

        csv_lines = []

        for line in lines:

            cells = [cell.strip() for cell in line.strip("|").split("|")]

            csv_lines.append(",".join(cells))

        csv_text = "\n".join(csv_lines)

        print("\nParsed Markdown Table")
        print("-" * 40)
        print(markdown)

        dataframe = pd.read_csv(
            io.StringIO(csv_text),
            dtype=str,
            keep_default_na=False,
        )

        dataframe.columns = [
            column.strip().lower().replace(" ", "_") for column in dataframe.columns
        ]

        dataframe = dataframe.fillna("")

        return dataframe
