"""
validate_kgw.py

Unit test for the KGW perfect-column solver in src/kgw.py, against the 42
published rows of KGW Table 1 (Köllner, Gardner & Wadee, 2023, Structures 56,
104844). Self-contained: needs only data/kgw_table1.csv.

The idea (area-invariant shape check)
-------------------------------------
Table 1 gives model loads P_C^mod in kN but no areas, so we cannot convert chi
to kN without fabricating one. Instead we exploit the table's structure: within
one family - fixed (ref, f_y, n), length varying - the section and material are
constant, so

    P_C^mod = chi_mod * A * f_y ,  with (A * f_y) constant across the family.

Hence P_C^mod is proportional to chi_mod within a family, and the quantity

    q = chi_solver / P_C^mod

is constant across a family IF the solver has the right slenderness dependence -
whatever the unknown (A * f_y) constant is. We normalise q by its family mean and
assert the residual scatter (pooled CoV) is small. This tests the *shape* of the
chi(lambda_bar) curve, which is what a solver bug distorts. No area is used.

Families are keyed on (ref, f_y, n) - the quantities that are exactly constant
within a block - not on measured (H, B), which wobble by ~0.1 mm and would split
each block into singletons that test nothing.

The ALPHA_RO guard
------------------
The shape test is nearly blind to a pure miscalibration of the Ramberg-Osgood
constant, since that rescales chi almost uniformly and barely moves the CoV
(empirically alpha_ro off by 2x only lifts the CoV from ~1.8% to ~3.4%). We
therefore also assert ALPHA_RO directly against the paper's value - a data-free
check that closes that gap.

Tolerance
---------
SHAPE_COV_TOL = 4% is an engineering margin: ~2x the observed error (~1.8%) and
well above the ~0.25% floor implied by Table 1's rounding, while low enough that
a functional-form error (e.g. a wrong power on lambda_bar) inflates the metric to
~20% and is caught immediately.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.kgw import chi_perfect, ALPHA_RO

BASE_DIR = Path(__file__).parent
TABLE1 = BASE_DIR / "data" / "validation" / "kgw_table1.csv"

SHAPE_COV_TOL = 0.04   # pooled within-family shape CoV must be below this


def _prepare() -> pd.DataFrame:
    """Load Table 1, run the solver, and form the area-free family-shape ratio."""
    t = pd.read_csv(TABLE1)
    t["E_MPa"] = t["E_0"] * 1000.0
    t["chi_solver"] = [
        chi_perfect(lb, n, E, fy)
        for lb, n, E, fy in zip(t.lambda_bar, t.n, t.E_MPa, t.f_y)
    ]
    t["family"] = (t["Ref"].astype(str) + " | fy=" + t["f_y"].astype(str) + " | n=" + t["n"].astype(str))
    t["q"] = t["chi_solver"] / t["P_mod_C"]          # (A*f_y) cancels on normalising
    t["q_norm"] = t.groupby("family")["q"].transform(lambda x: x / x.mean())
    return t


def family_report(t: pd.DataFrame) -> pd.DataFrame:
    """Per-family breakdown: size, slenderness span, within-family scatter."""
    return t.groupby("family").agg(
        n_rows=("q", "size"),
        lambda_min=("lambda_bar", "min"),
        lambda_max=("lambda_bar", "max"),
        within_family_cov_pct=("q", lambda x: 100 * x.std() / x.mean() if len(x) > 1 else 0.0),
    ).round(4)


def validate(verbose: bool = True) -> pd.DataFrame:
    """Assert the solver reproduces KGW Table 1. Returns the per-row frame."""
    t = _prepare()
    shape_cov = float(t["q_norm"].std())
    shape_max = float((t["q_norm"] - 1.0).abs().max())

    if verbose:
        print("KGW Table 1 solver validation (area-invariant shape check)")
        print(f"  rows verified                 : {len(t)} across {t.family.nunique()} "
              f"families (100% of Table 1)")
        print(f"  pooled within-family shape CoV: {100*shape_cov:.2f} %  "
              f"(assert < {SHAPE_COV_TOL*100:.0f} %)")
        print(f"  max within-family deviation   : {100*shape_max:.2f} %")
        print(f"  ALPHA_RO                       : {ALPHA_RO}  (assert == 0.002)")
        print()
        print("  per-family detail:")
        print("    " + family_report(t).to_string().replace("\n", "\n    "))

    assert shape_cov < SHAPE_COV_TOL, \
        f"within-family shape CoV {100*shape_cov:.2f}% exceeds {SHAPE_COV_TOL*100:.0f}%"
    assert ALPHA_RO == 0.002, \
        f"ALPHA_RO={ALPHA_RO} must equal 0.002 (KGW Eq. 1, 0.2% offset strain)"

    if verbose:
        print("\n  PASS - solver reproduces KGW model shape across all 42 rows.")
    return t


if __name__ == "__main__":
    validate()