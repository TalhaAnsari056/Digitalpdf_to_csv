import re
from pathlib import Path


class NormalizationService:

    @staticmethod
    def normalize(document):

        output = []

        for row in document.rows:

            row.cells = NormalizationService.tokenize(row.text)

            output.append(row)

        folder = Path(document.filepath).parent.parent / "output"

        return document

    @staticmethod
    def tokenize(text):

        text = text.replace("|", " | ")

        text = re.sub(r"\s+", " ", text)

        tokens = text.split()

        cells = []

        current = []

        for token in tokens:

            if token == "|":

                if current:

                    cells.append(" ".join(current))

                    current = []

            else:

                current.append(token)

        if current:

            cells.append(" ".join(current))

        return cells
