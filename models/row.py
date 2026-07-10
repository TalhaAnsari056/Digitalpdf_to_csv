from dataclasses import dataclass, field

from models.cell import CellData


@dataclass
class RowData:

    row_number: int

    page_number: int

    # cells: list[CellData] = field(default_factory=list)

    cells: list[str] = field(default_factory=list)

    text: str = ""
