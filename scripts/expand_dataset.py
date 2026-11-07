
import csv
import shutil
from pathlib import Path
from collections import Counter

BASE = Path(r"C:\Users\Admin\BCA152-Baby-Monitor\Datasets")

METADATA = BASE / "ESC-50-master" / "meta" / "esc50.csv"
AUDIO = BASE / "ESC-50-master" / "audio"
OUTPUT = BASE / "EdgeImpulse-Split" / "training" / "not_crying"

# Add more varied sounds without including the held-out fold 5.
CATEGORIES = {
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
    "dog",
    "cat",
    "chirping_birds",
    "rain",
    "wind",
    "thunderstorm",
    "door_wood_creaks",
    "keyboard_typing",
    "mouse_click",
    "clock_alarm",
}

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from math import gcd

with METADATA.open(newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

counts = Counter()

for row in rows:
    if row["category"] not in CATEGORIES:
        continue

    if int(row["fold"]) == 5:
        continue

    source = AUDIO / row["filename"]
    destination = OUTPUT / row["filename"]

    if destination.exists():
        counts["already_present"] += 1
        continue

    audio, sample_rate = sf.read(source, dtype="float32")

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    divisor = gcd(sample_rate, 16000)

    converted = resample_poly(
        audio,
        16000 // divisor,
        sample_rate // divisor
    )

    converted = np.clip(converted, -1.0, 1.0)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    sf.write(destination, converted, 16000, subtype="PCM_16")

    counts["added"] += 1

print("Expansion complete!")
print("New not_crying recordings:", counts["added"])
print("Already present:", counts["already_present"])
print("Total not_crying training files:", len(list(OUTPUT.glob("*.wav"))))
