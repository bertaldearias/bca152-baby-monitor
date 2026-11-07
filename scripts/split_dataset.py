
import csv
import shutil
from pathlib import Path

BASE = Path(r"C:\Users\Admin\BCA152-Baby-Monitor\Datasets")
SOURCE = BASE / "EdgeImpulse-Ready"
METADATA = BASE / "ESC-50-master" / "meta" / "esc50.csv"
OUTPUT = BASE / "EdgeImpulse-Split"

with METADATA.open(newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

folds = {row["filename"]: int(row["fold"]) for row in rows}

counts = {}

for label in ["crying", "not_crying"]:
    for source_file in (SOURCE / label).glob("*.wav"):
        fold = folds[source_file.name]
        subset = "testing" if fold == 5 else "training"

        destination = OUTPUT / subset / label / source_file.name
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source_file, destination)
        counts[(subset, label)] = counts.get((subset, label), 0) + 1

print("Dataset split complete!")

for subset in ["training", "testing"]:
    for label in ["crying", "not_crying"]:
        print(f"{subset}/{label}: {counts.get((subset, label), 0)} files")

print("Output:", OUTPUT)
