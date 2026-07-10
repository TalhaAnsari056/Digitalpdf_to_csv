from dataclasses import dataclass, field


@dataclass
class WordData:

    text: str

    x0: float
    y0: float
    x1: float
    y1: float

    block_no: int
    line_no: int
    word_no: int


@dataclass
class PageData:

    page_number: int

    text: str = ""

    words: list[WordData] = field(default_factory=list)


@dataclass
class Document:

    filename: str

    filepath: str

    pages: list[PageData] = field(default_factory=list)

    document_type: str | None = None

    parsed_data: list = field(default_factory=list)
