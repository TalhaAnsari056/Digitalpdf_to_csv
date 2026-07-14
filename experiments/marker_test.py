from pathlib import Path
import subprocess
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent

pdf = PROJECT_ROOT / "input" / "pdfs" / "BankStatement.pdf"

output = PROJECT_ROOT / "output" / "marker"

output.mkdir(parents=True, exist_ok=True)

start = time.perf_counter()

command = [
    "marker_single",
    str(pdf),
    "--output_dir",
    str(output),
    # ======================================================
    # OCR CONFIGURATION
    # ======================================================
    # ---------- OCR ENABLED ----------
    # Leave the flags below commented.
    # ---------- OCR DISABLED ----------
    "--DocumentBuilder_disable_ocr",
    "--LineBuilder_disable_ocr",
    "--TableProcessor_disable_ocr",
    # ======================================================
]

print("Running command:")
print(" ".join(command))
print()

subprocess.run(command, check=True)

elapsed = time.perf_counter() - start

with open(output / "execution_time.txt", "w") as f:
    f.write(f"{elapsed:.2f} seconds")

print(f"\nFinished in {elapsed:.2f} seconds")
