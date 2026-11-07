
import csv
import random
import wave
from pathlib import Path
from collections import Counter

# Change this path if your extracted folder is elsewhere.
DATASET = Path(r"C:\Users\Admin\BCA152-Baby-Monitor\Datasets\ESC-50-master")
OUTPUT = DATASET.parent / "EdgeImpulse-Ready"

AUDIO = DATASET / "audio"
METADATA = DATASET / "meta" / "esc50.csv"

# ESC-50 includes 40 crying_baby clips.
# Use a balanced starting dataset: 40 crying + 40 non-crying.
NEGATIVE_CATEGORIES = [
    "laughing",
    "breathing",
    "coughing",
    "sneezing",
    "snoring",
    "clock_tick",
    "vacuum_cleaner",
    "washing_machine",
    "pouring_water",
    "door_wood_knock",
]

random.seed(42)

with METADATA.open(newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

crying = [
    row for row in rows
    if row["category"] == "crying_baby"
]

not_crying = [
    row for row in rows
    if row["category"] in NEGATIVE_CATEGORIES
]

# Select four examples from each negative category.
selected_negative = []

for category in NEGATIVE_CATEGORIES:
    candidates = [
        row for row in not_crying
        if row["category"] == category
    ]
    selected_negative.extend(random.sample(candidates, 4))

selected = [
    ("crying", row) for row in crying
] + [
    ("not_crying", row) for row in selected_negative
]

# Convert ESC-50's 44.1 kHz WAV audio to 16 kHz mono.
# Requires: pip install numpy scipy soundfile
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

counts = Counter()

for label, row in selected:
    source = AUDIO / row["filename"]
    destination = OUTPUT / label / row["filename"]
    destination.parent.mkdir(parents=True, exist_ok=True)

    audio, sample_rate = sf.read(source, dtype="float32")

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    from math import gcd
    divisor = gcd(sample_rate, 16000)

    converted = resample_poly(
        audio,
        16000 // divisor,
        sample_rate // divisor
    )

    converted = np.clip(converted, -1.0, 1.0)

    sf.write(destination, converted, 16000, subtype="PCM_16")
    counts[label] += 1

print("Dataset preparation complete!")
print("Crying recordings:", counts["crying"])
print("Non-crying recordings:", counts["not_crying"])
print("Output folder:", OUTPUT)
