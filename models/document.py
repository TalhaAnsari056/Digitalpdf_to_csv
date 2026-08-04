from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Document:

    filename: str

    filepath: str

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

    mapped_markdown: str = ""
    mapped_markdown_path: str = ""

    validated_markdown: str = ""
    validated_markdown_path: str = ""

    metadata_prompt: str = ""
    metadata_prompt_path: str = ""

    raw_metadata_response: str = ""
    raw_metadata_response_path: str = ""

    metadata: dict = field(default_factory=dict)
    metadata_path: str = ""

    hierarchy: dict = field(default_factory=dict)
    hierarchy_path: str = ""

    hierarchy_prompt: str = ""
    hierarchy_prompt_path: str = ""

    raw_hierarchy_response: str = ""
    raw_hierarchy_response_path: str = ""

    extraction_report: dict = field(default_factory=dict)
    extraction_report_path: str = ""

    financial_summary: dict = field(default_factory=dict)
    financial_summary_path: str = ""

    financial_summary_prompt: str = ""
    financial_summary_prompt_path: str = ""

    raw_financial_summary_response: str = ""
    raw_financial_summary_response_path: str = ""

    financial_summary_report: dict = field(default_factory=dict)
    financial_summary_report_path: str = ""

    financial_analytics: dict = field(default_factory=dict)
    financial_analytics_path: str = ""

    financial_analytics_report: dict = field(default_factory=dict)
    financial_analytics_report_path: str = ""

    memory_prompt: str = ""
    memory_prompt_path: str = ""

    raw_memory_response: str = ""
    raw_memory_response_path: str = ""

    memory: dict = field(default_factory=dict)
    memory_path: str = ""

    memory_report: dict = field(default_factory=dict)
    memory_report_path: str = ""

    memory_store_path: str = ""
    memory_store_entry: dict = field(default_factory=dict)

    memory_store_report: dict = field(default_factory=dict)
    memory_store_report_path: str = ""

    document_id: str = ""
    memory_index: int = 0

    dataframe: object | None = None
    dataframe_path: str = ""

    normalized_dataframe: object | None = None
    normalized_dataframe_path: str = ""

    # LLM output
    # mapped_json: dict = field(default_factory=dict)
    parsed_rows: list = field(default_factory=list)
    # Validation output
    validation_report: dict = field(default_factory=dict)
    validation_report_path: str = ""

    # CSV
    csv_path: str = ""
    excel_path: str = ""
    response: dict = field(default_factory=dict)
    response_path: str = ""
