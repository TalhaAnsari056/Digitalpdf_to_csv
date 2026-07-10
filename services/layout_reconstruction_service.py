from collections import defaultdict

from models.row import RowData
from models.cell import CellData


class LayoutReconstructionService:

    Y_TOLERANCE = 3

    @staticmethod
    def reconstruct(document):

        rows = []

        row_number = 1

        for page in document.pages:

            groups = defaultdict(list)

            for word in page.words:

                key = round(word.y0 / LayoutReconstructionService.Y_TOLERANCE)

                groups[key].append(word)

            for key in sorted(groups.keys()):

                words = sorted(groups[key], key=lambda w: w.x0)

                cells = []

                current_words = []

                previous_x = None

                for word in words:

                    if previous_x is None:

                        current_words.append(word)

                    elif word.x0 - previous_x > 40:

                        cells.append(
                            LayoutReconstructionService.build_cell(current_words)
                        )

                        current_words = [word]

                    else:

                        current_words.append(word)

                    previous_x = word.x1

                if current_words:

                    cells.append(LayoutReconstructionService.build_cell(current_words))

                rows.append(
                    RowData(
                        row_number=row_number,
                        page_number=page.page_number,
                        cells=cells,
                        text=" | ".join(cell.text for cell in cells),
                    )
                )

                row_number += 1

        return rows

    @staticmethod
    def build_cell(words):

        return CellData(
            text=" ".join(word.text for word in words),
            x0=min(word.x0 for word in words),
            x1=max(word.x1 for word in words),
            y0=min(word.y0 for word in words),
            y1=max(word.y1 for word in words),
        )
