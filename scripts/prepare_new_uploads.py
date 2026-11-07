
import shutil
from pathlib import Path

BASE = Path(r"C:\Users\Admin\BCA152-Baby-Monitor\Datasets")

ORIGINAL = BASE / "EdgeImpulse-Ready" / "not_crying"
BALANCED = BASE / "EdgeImpulse-Balanced" / "not_crying"
OUTPUT = BASE / "EdgeImpulse-New-Uploads" / "not_crying"

OUTPUT.mkdir(parents=True, exist_ok=True)

original_names = {file.name for file in ORIGINAL.glob("*.wav")}

count = 0

for file in BALANCED.glob("*.wav"):
    if file.name not in original_names:
        shutil.copy2(file, OUTPUT / file.name)
        count += 1

print("New recordings ready:", count)
print("Output:", OUTPUT)
