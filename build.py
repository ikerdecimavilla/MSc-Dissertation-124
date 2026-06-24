from pathlib import Path
import numpy as np
import pandas as pd
from src.features import add_features
from src.classify import classify

# Anchor paths relative to this script's exact location
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED = DATA_DIR / "extracted"
PROCESSED = DATA_DIR / "processed"


def _validate(master):
    """Loud, build-time integrity checks on the assembled master frame.

    Each of these would have caught one of the bugs found during validation, so
    a build that silently 'succeeds' with a corrupt master is no longer possible.
    """
    # 1. Major axis must carry the larger inertia, by definition.
    swapped = master["I_major"] < master["I_minor"] - 1e-9
    assert not swapped.any(), \
        f"I_major < I_minor for: {master.loc[swapped, 'specimen_id'].tolist()}"

    # 2. lambda_bar dual-formula guard: sqrt(N_y/N_cr) must agree with the
    #    closed form (Le/(pi*R)) * sqrt(sigma_02/E0). Catches unit/scaling slips.
    lbar_alt = (master["Le"] / (np.pi * master["R"])) * \
        np.sqrt(master["sigma_02"] / master["E0"])
    assert np.allclose(master["lambda_bar"], lbar_alt, rtol=1e-6), \
        "lambda_bar disagrees with its closed-form equivalent (unit error?)"

    # 3. Welded open sections must use the 0.20 plateau (EN 1993-1-4 Table 5.3).
    welded_open = master["section_type"].isin(["I", "H"]) & \
        master["forming_route"].isin(["welded", "laser_welded"])
    bad_l0 = welded_open & (master["lambda_0"] != 0.20)
    assert not bad_l0.any(), \
        f"welded open section with lambda_0 != 0.20: {master.loc[bad_l0, 'specimen_id'].tolist()}"

    # 4. Total imperfection is a magnitude and must be non-negative.
    neg = master["w_total"] < 0
    assert not neg.any(), \
        f"negative w_total for: {master.loc[neg, 'specimen_id'].tolist()}"


def build():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frames = []

    csv_files = list(EXTRACTED.glob("*.csv"))
    if not csv_files:
        return print(f"No CSVs found in {EXTRACTED}. Pipeline halted.")

    for csv in sorted(csv_files):
        print(f"Processing: {csv.name}")
        df = pd.read_csv(csv)

        df = df.dropna(subset=["section_type"])

        enriched = add_features(df)      # geometry + mechanics (A, I, lambda_bar, ...)
        classified = classify(enriched)  # EN 1993-1-4 class + inferred_failure_mode
        classified.to_csv(PROCESSED / csv.name, index=False)
        frames.append(classified)

    # Combine, validate, and save master dataset
    if frames:
        master = pd.concat(frames, ignore_index=True)
        _validate(master)
        master.to_csv(DATA_DIR / "master.csv", index=False)
        print("Success! master.csv updated.")


if __name__ == "__main__":
    build()