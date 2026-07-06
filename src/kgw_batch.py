"""
kgw_batch.py

Batch application of the verified KGW solver (src/kgw.py, verified by
src/kgw_verification.py against KGW Table 1) across the master dataset.

Runs as the final stage of build.py, so master.csv is always complete and
identical on rebuild; also runnable standalone during development:

    python -m src.kgw_batch        # re-runs predictions on data/master.csv

Appended columns
----------------
chi_perfect           KGW strength reduction factor, perfect column (beta = 1).
                      NOT capped at 1: chi > 1 is real strain-hardening reserve.
chi_kgw               KGW factor with the Eq. 19 correction beta(lambda_bar)
                      applied inside the solve (m = beta*n). Not capped.
chi_eurocode          EN 1993-1-4 6.3 flexural buckling curve, alpha/lambda_0
                      mapped per Table 5.3 (classify.imperfection_factor /
                      the existing lambda_0 column). Capped at 1 per the code.
N_perfect, N_kgw,     chi * N_squash [kN]. N_squash is already on the A_eff
N_eurocode            basis for Class 4 sections, so no special-casing here.
kgw_convergence_flag  True where the KGW solves converged and passed
                      post-verification; False rows carry NaN outputs and a
                      logged reason, and never crash the batch.

Numerical safety (three deterministic layers)
---------------------------------------------
1. pre-validation: rows with missing/non-positive lambda_bar, n, E0, sigma_02
   or N_squash short-circuit to NaN + flag False (reason 'invalid_input:...').
2. guarded solve: ValueError (kgw.py input guard) and RuntimeError (bracket /
   brentq failure) are caught per row, logged with specimen_id, NaN'd.
3. post-verification: every converged root is substituted back into the
   governing equation (|g| < 1e-10, reusing kgw_verification.equation_residual
   with m = beta*n for the corrected solve), checked against the Euler bound
   chi <= 1/lambda_bar^2, and - for lambda_bar >= lambda_t = 0.9, where the
   correction can only reduce strength - chi_kgw <= chi_perfect. (Below the
   transition slenderness the correction legitimately *increases* the load,
   KGW Fig. 8, so no ordering is asserted there.)
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from .classify import imperfection_factor
from .kgw import BETA_LAMBDA_T, beta_kgw, chi_corrected, chi_perfect
from .kgw_verification import EQ_RESIDUAL_TOL, equation_residual

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MASTER = BASE_DIR / "data" / "master.csv"

_REQUIRED = ("lambda_bar", "n", "E0", "sigma_02", "N_squash")
_EULER_TOL = 1e-9            # relative headroom on the chi <= 1/lambda^2 bound


def chi_eurocode(lambda_bar, alpha, lambda_0):
    """EN 1993-1-4 6.3.1 flexural buckling curve (capped at 1.0).

    chi = 1 / (phi + sqrt(phi^2 - lambda_bar^2)) <= 1,
    phi = 0.5 * (1 + alpha*(lambda_bar - lambda_0) + lambda_bar^2),
    with chi = 1 on the plateau lambda_bar <= lambda_0. NaN inputs propagate.
    """
    lb = np.asarray(lambda_bar, dtype=float)
    a = np.asarray(alpha, dtype=float)
    l0 = np.asarray(lambda_0, dtype=float)
    phi = 0.5 * (1.0 + a * (lb - l0) + lb**2)
    with np.errstate(invalid="ignore"):
        chi = 1.0 / (phi + np.sqrt(phi**2 - lb**2))
        chi = np.minimum(chi, 1.0)
        return np.where(lb <= l0, 1.0, chi)


def _solve_row(row):
    """KGW solves for one row. Returns (chi_p, chi_k, converged, reason)."""
    # layer 1: pre-validation
    for col in _REQUIRED:
        v = row[col]
        if pd.isna(v) or v <= 0:
            return np.nan, np.nan, False, f"invalid_input:{col}={v!r}"

    lb, n = float(row["lambda_bar"]), float(row["n"])
    E, fy = float(row["E0"]), float(row["sigma_02"])

    # layer 2: guarded solve
    try:
        chi_p = chi_perfect(lb, n, E, fy)
        chi_k = chi_corrected(lb, n, E, fy)
    except (ValueError, RuntimeError) as exc:
        return np.nan, np.nan, False, f"solver:{type(exc).__name__}:{exc}"

    # layer 3: post-verification
    beta = float(beta_kgw(lb))
    g_p = abs(equation_residual(lb, n, E, fy, chi_p))
    g_k = abs(equation_residual(lb, beta * n, E, fy, chi_k))
    if max(g_p, g_k) >= EQ_RESIDUAL_TOL:
        return np.nan, np.nan, False, f"residual:|g|={max(g_p, g_k):.2e}"
    euler = (1.0 / lb**2) * (1.0 + _EULER_TOL)
    if not (0.0 < chi_p <= euler and 0.0 < chi_k <= euler):
        return np.nan, np.nan, False, "bounds:chi outside (0, 1/lambda^2]"
    if lb >= BETA_LAMBDA_T and chi_k > chi_p * (1.0 + _EULER_TOL):
        return np.nan, np.nan, False, "ordering:chi_kgw > chi_perfect"

    return chi_p, chi_k, True, ""


def add_predictions(df):
    """Append the KGW and Eurocode predictions to a master-format frame.

    Pure function: no I/O. Requires the master computed columns (lambda_bar,
    N_squash, lambda_0, section_type, forming_route, buckling_axis).
    """
    out = df.copy()

    results = [_solve_row(row) for _, row in out.iterrows()]
    out["chi_perfect"] = [r[0] for r in results]
    out["chi_kgw"] = [r[1] for r in results]
    out["kgw_convergence_flag"] = [r[2] for r in results]

    for (_, row), (_, _, ok, reason) in zip(out.iterrows(), results):
        if not ok:
            log.warning("KGW solve skipped for %s: %s",
                        row.get("specimen_id", "<no id>"), reason)

    alpha = out.apply(imperfection_factor, axis=1)
    out["chi_eurocode"] = chi_eurocode(out["lambda_bar"], alpha, out["lambda_0"])

    for chi_col, n_col in (("chi_perfect", "N_perfect"),
                           ("chi_kgw", "N_kgw"),
                           ("chi_eurocode", "N_eurocode")):
        out[n_col] = out[chi_col] * out["N_squash"]

    n_ok = int(out["kgw_convergence_flag"].sum())
    log.info("KGW batch: %d/%d rows converged", n_ok, len(out))
    return out


def convergence_summary(df):
    """Per-source convergence counts (for the build log / notebook record)."""
    return df.groupby("source_id").agg(
        n_rows=("kgw_convergence_flag", "size"),
        n_converged=("kgw_convergence_flag", "sum"),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    master = pd.read_csv(MASTER)
    master = add_predictions(master)
    master.to_csv(MASTER, index=False)
    print(convergence_summary(master).to_string())
    n_ok = int(master["kgw_convergence_flag"].sum())
    print(f"KGW batch complete: {n_ok}/{len(master)} rows converged; "
          f"master.csv updated.")
