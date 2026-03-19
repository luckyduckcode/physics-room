from __future__ import annotations

import numpy as np


def ladder_ops(N: int) -> tuple[np.ndarray, np.ndarray]:
    assert N > 1, f"N must be > 1, got {N}"
    A = np.zeros((N, N), dtype=complex)
    for n in range(1, N):
        A[n - 1, n] = np.sqrt(float(n))
    return A, A.conj().T


def mat_power(M: np.ndarray, n: int) -> np.ndarray:
    assert n >= 0, "n must be >= 0"
    if n == 0:
        return np.eye(M.shape[0], dtype=complex)
    if n == 1:
        return M.copy()
    out = M.copy()
    for _ in range(n - 1):
        out = out @ M
    return out


def position_op(N: int) -> np.ndarray:
    A, Ad = ladder_ops(N)
    return (A + Ad) / np.sqrt(2.0)


def momentum_op(N: int) -> np.ndarray:
    A, Ad = ladder_ops(N)
    return 1j * (Ad - A) / np.sqrt(2.0)


def number_op(N: int) -> np.ndarray:
    A, Ad = ladder_ops(N)
    return Ad @ A


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B - B @ A


def check_hermitian(M: np.ndarray, tol: float = 1e-10) -> bool:
    return bool(np.max(np.abs(M - M.conj().T)) < tol)
