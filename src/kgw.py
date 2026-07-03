"""
Reduces the KGW energy-formulation to a scalar root-finding problem in chi.
Exposes perfect-column predictions (beta = 1) and KGW corrections.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

# Ramberg-Osgood 0.2% offset strain constant
ALPHA_RO: float = 0.002

#  KGW Eq.19 correction constants
BETA_A0: float = 5.0
BETA_A1: float = 0.275
BETA_A2: float = 0.725
BETA_LAMBDA_T: float = 0.9


# Correction factor B
def beta_kgw(lambda_bar, *, cap_unity: bool = True):
    """
    KGW Eq.19 correction factor for global flexural buckling.
    Returns a scalar or array of beta values, with the same shape as lambda_bar.
    """
    lb = np.asarray(lambda_bar, dtype=float)
    beta = BETA_A1 * np.tanh(BETA_A0 * (BETA_LAMBDA_T - lb)) + BETA_A2
    if cap_unity:
        beta = np.minimum(beta, 1.0)
    return beta if beta.ndim else float(beta)

# Scalar root find
def _chi_root(lambda_bar: float, n: float, Delta: float, beta: float = 1.0) -> float:
    """Solve g_beta(chi) = 0 for the single positive root. Scalar inputs only."""
    if not (lambda_bar > 0 and n > 0 and Delta > 0 and beta > 0):
        raise ValueError(
            f"invalid inputs: lambda_bar={lambda_bar}, n={n}, Delta={Delta}, beta={beta}"
        )
    m = beta * n
    k = m * ALPHA_RO / Delta
    rhs = 1.0 / lambda_bar ** 2

    def g(chi: float) -> float:
        return k * chi ** m + chi - rhs

    # g is strictly increasing; expand the upper bracket until it changes sign.
    hi = 1.0
    for _ in range(200):
        if g(hi) >= 0.0:
            break
        hi *= 2.0
    else:  # pragma: no cover - would require absurd inputs
        raise RuntimeError(f"failed to bracket root (lambda_bar={lambda_bar}, n={n})")

    return brentq(g, 1e-12, hi, xtol=1e-14, rtol=1e-12, maxiter=200)

# Chi for B=1 (perfect column)
def chi_perfect(lambda_bar: float, n: float, E: float, f_y: float, *, cap_squash: bool = False) -> float:
    """
    Perfect-column strength reduction factor chi (beta = 1).
    Real specimens sit below this
    """
    chi = _chi_root(lambda_bar, n, f_y / E, beta=1.0)
    return min(chi, 1.0) if cap_squash else chi

# Chi for B < 1 (KGW correction)
def chi_corrected(lambda_bar: float, n: float, E: float, f_y: float, *, cap_squash: bool = False) -> float:
    """
    KGW univariate-corrected chi applying beta(lambda_bar) to n.
    """
    beta = beta_kgw(lambda_bar)
    chi = _chi_root(lambda_bar, n, f_y / E, beta=beta)
    return min(chi, 1.0) if cap_squash else chi

# Vectorised helpers for dataframes
def chi_perfect_series(lambda_bar, n, E, f_y, *, cap_squash: bool = False):
    """Row-wise chi_perfect over array-likes. Returns an ndarray."""
    lb, nn, EE, fy = map(lambda x: np.asarray(x, dtype=float),
                         (lambda_bar, n, E, f_y))
    return np.array([chi_perfect(a, b, c, d, cap_squash=cap_squash)
                     for a, b, c, d in zip(lb, nn, EE, fy)])
 
 
def chi_corrected_series(lambda_bar, n, E, f_y, *, cap_squash: bool = False):
    """Row-wise chi_corrected over array-likes. Returns an ndarray."""
    lb, nn, EE, fy = map(lambda x: np.asarray(x, dtype=float),
                         (lambda_bar, n, E, f_y))
    return np.array([chi_corrected(a, b, c, d, cap_squash=cap_squash)
                     for a, b, c, d in zip(lb, nn, EE, fy)])
 