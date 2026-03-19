from __future__ import annotations

from typing import Callable, Optional

import numpy as np

from .operators import ladder_ops, mat_power, position_op, momentum_op


def build_H(
    N: int = 40,
    hbar: float = 1.0,
    omega: float = 1.0,
    phi: float = float(np.e),
    F: Optional[np.ndarray] = None,
    g: Optional[np.ndarray] = None,
    h: Optional[np.ndarray] = None,
    lam: float = 0.0,
    kappa: float = 0.0,
    Vcosmo: Optional[Callable] = None,
    f_t: float = 0.0,
) -> np.ndarray:
    A, Ad = ladder_ops(N)
    x = position_op(N)
    p = momentum_op(N)
    Nc = N - 1

    if F is None:
        F = np.ones(N + 1)
    if g is None:
        g = np.zeros(N)
    if h is None:
        h = np.zeros((N, N))

    H = np.zeros((N, N), dtype=complex)

    # Term 1: sum_n hbar*omega * F_{n+1} * (Ad)^n A^n
    for n in range(Nc + 1):
        H += hbar * omega * F[n + 1] * (mat_power(Ad, n) @ mat_power(A, n))

    # Term 2: 0.5 * (ln phi)^2 * (p^2 + x^2)
    c  = 0.5 * (np.log(phi) ** 2)
    H += c * (p @ p + x @ x)

    # Term 3: cosmological potential V(x)
    if Vcosmo is not None:
        H += Vcosmo(x)

    # Term 4: lambda * sum_n g_n * (Ad)^n A^n * f(t)
    if lam != 0.0:
        for n in range(Nc + 1):
            H += lam * g[n] * (mat_power(Ad, n) @ mat_power(A, n)) * f_t

    # Term 5: kappa * sum_{n,m} h_nm * [(Ad)^n A^m + (Ad)^m A^n] * (-1)^(n-m)
    if kappa != 0.0:
        for n in range(Nc + 1):
            for m in range(Nc + 1):
                parity = (-1) ** (n - m)
                term   = (mat_power(Ad, n) @ mat_power(A, m) +
                          mat_power(Ad, m) @ mat_power(A, n))
                H     += kappa * h[n, m] * parity * term

    return 0.5 * (H + H.conj().T)
