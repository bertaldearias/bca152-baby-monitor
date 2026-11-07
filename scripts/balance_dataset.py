
import csv
import random
import shutil
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path(r"C:\Users\Admin\BCA152-Baby-Monitor\Datasets")
META = BASE / "ESC-50-master" / "meta" / "esc50.csv"
SOURCE = BASE / "EdgeImpulse-Split" / "training"
OUTPUT = BASE / "EdgeImpulse-Balanced"

random.seed(42)

with META.open(newline="", encoding="utf-8") as f:
    metadata = {
        row["filename"]: row
        for row in csv.DictReader(f)
    }

# Preserve all 32 crying training files.
crying_files = sorted((SOURCE / "crying").glob("*.wav"))

# Group negative recordings by sound category.
categories = defaultdict(list)

for file in (SOURCE / "not_crying").glob("*.wav"):
    info = metadata[file.name]

    if int(info["fold"]) != 5:
        categories[info["category"]].append(file)

# Select across categories in rounds for diversity.
for files in categories.values():
    random.shuffle(files)

selected = []
category_names = sorted(categories)

while len(selected) < 64:
    added = False

    for category in category_names:
        if categories[category] and len(selected) < 64:
            selected.append(categories[category].pop())
            added = True

    if not added:
        break

# Rebuild the balanced output to avoid stale files.
if OUTPUT.exists():
    shutil.rmtree(OUTPUT)

for label, files in [
    ("crying", crying_files),
    ("not_crying", selected),
]:
    folder = OUTPUT / label
    folder.mkdir(parents=True, exist_ok=True)

    for file in files:
        shutil.copy2(file, folder / file.name)

print("Balanced dataset ready!")
print("Crying:", len(crying_files))
print("Not crying:", len(selected))
print("Output:", OUTPUT)
