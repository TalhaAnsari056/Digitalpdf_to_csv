from pathlib import Path
import time

from services.prompt_builder_service import PromptBuilderService
from services.llm_service import LLMService

# ==========================================================
# CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENT_TYPE = "balance_sheet"
# DOCUMENT_TYPE = "bank_statement"

MARKDOWN_FILE = (
    PROJECT_ROOT
    / "output"
    / "Balance-Sheet-Example_digitalPDF_6-"
    / "cleaned"
    / "cleaned_markdown.md"
)

PDF_NAME = MARKDOWN_FILE.parents[1].name

MODEL_NAME = LLMService.MODEL.replace("/", "_").replace(":", "_")

OUTPUT_DIR = PROJECT_ROOT / "output" / "llm_test" / PDF_NAME / MODEL_NAME
# OUTPUT_DIR = PROJECT_ROOT / "output" / "llm_test"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# LOAD MARKDOWN
# ==========================================================

with open(MARKDOWN_FILE, "r", encoding="utf-8") as file:
    markdown = file.read()

# ==========================================================
# BUILD PROMPT
# ==========================================================

if DOCUMENT_TYPE == "balance_sheet":

    prompt = PromptBuilderService.build_balance_sheet_prompt(markdown)

elif DOCUMENT_TYPE == "bank_statement":

    prompt = PromptBuilderService.build_bank_statement_prompt(markdown)

else:

    raise ValueError("Unsupported document type.")

# ==========================================================
# SAVE PROMPT
# ==========================================================

with open(
    OUTPUT_DIR / "prompt.txt",
    "w",
    encoding="utf-8",
) as file:

    file.write(prompt)

# ==========================================================
# RUN LLM
# ==========================================================

start = time.perf_counter()

response = LLMService.generate(prompt)

elapsed = time.perf_counter() - start

# ==========================================================
# SAVE RESPONSE
# ==========================================================

with open(
    OUTPUT_DIR / "standardized_markdown.md",
    "w",
    encoding="utf-8",
) as file:

    file.write(response)

# ==========================================================
# SAVE MODEL INFO
# ==========================================================

with open(
    OUTPUT_DIR / "model.txt",
    "w",
    encoding="utf-8",
) as file:

    file.write(LLMService.MODEL)

# ==========================================================
# SAVE EXECUTION STATS
# ==========================================================

stats = f"""
Model               : {LLMService.MODEL}
Document            : {PDF_NAME}
Document Type       : {DOCUMENT_TYPE}

Execution Time      : {elapsed:.2f} seconds

Prompt Characters   : {len(prompt):,}
Response Characters : {len(response):,}
"""

with open(
    OUTPUT_DIR / "execution_stats.txt",
    "w",
    encoding="utf-8",
) as file:

    file.write(stats)

# ==========================================================
# TERMINAL
# ==========================================================

print()
print("=" * 60)
print("LLM TEST COMPLETED")
print("=" * 60)
print(stats)

print("Results saved to:")
print(OUTPUT_DIR)
