from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Document:

    filename: str

    filepath: str

    # Marker output
    markdown_path: str = ""

    markdown: str = ""
    markdown_path: str = ""

    # Cleaner output
    cleaned_markdown: str = ""
    cleaned_markdown_path: str = ""

    # Rule-based classifier result
    document_type: str | None = None

    prompt: str = ""
    prompt_path: str = ""

    llm_response: str = ""
    llm_response_path: str = ""

    structured_data: dict = field(default_factory=dict)
    structured_data_path: str = ""

    # LLM output
    mapped_json: dict = field(default_factory=dict)

    # Validation output
    validation_report: dict = field(default_factory=dict)
    validation_report_path: str = ""
    # CSV
    csv_path: str = ""
