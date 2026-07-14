from pathlib import Path
import time

from liteparse import LiteParse

pdf = Path("input/pdfs/Balance-Sheet-Example_digitalPDF.pdf")

output_dir = Path("output/liteparse")
output_dir.mkdir(parents=True, exist_ok=True)

parser = LiteParse(
    ocr_enabled=False,
)

start = time.time()

result = parser.parse(pdf)

elapsed = time.time() - start

print("=" * 70)
print("LiteParse Finished")
print("=" * 70)

print(type(result))

print(result)

print(f"\nExecution Time : {elapsed:.2f} sec")

# Save raw output
with open(output_dir / "raw_output.txt", "w", encoding="utf-8") as f:
    f.write(str(result))

print("\nSaved raw output.")
