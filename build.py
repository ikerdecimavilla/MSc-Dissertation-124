from pathlib import Path
import pandas as pd
from src.features import add_features
from src.classify import classify

# Anchor paths relative to this script's exact location
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED = DATA_DIR / "extracted"
PROCESSED = DATA_DIR / "processed"

def build():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frames = []

    csv_files = list(EXTRACTED.glob("*.csv"))
    if not csv_files:
        return print(f"No CSVs found in {EXTRACTED}. Pipeline halted.")

    for csv in sorted(csv_files):
        print(f"Processing: {csv.name}")
        df = pd.read_csv(csv)

        enriched = add_features(df)      # geometry + mechanics (A, I, lambda_bar, ...)
        classified = classify(enriched)  # EN 1993-1-4 class + inferred_failure_mode
        classified.to_csv(PROCESSED / csv.name, index=False)
        frames.append(classified)

    # Combine and save master dataset
    if frames:
        master = pd.concat(frames, ignore_index=True)
        master.to_csv(PROCESSED / "master.csv", index=False)
        print("Success! master.csv updated.")

if __name__ == "__main__":
    build()