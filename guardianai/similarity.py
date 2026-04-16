from __future__ import annotations

import numpy as np


def cosine_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """a: (n, d), b: (m, d), rows L2-normalized. Returns (n, m) cosine similarities."""
    if a.size == 0 or b.size == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype=np.float32)
    return a @ b.T


def best_match_score(query_embs: np.ndarray, candidate_embs: np.ndarray) -> tuple[float, int, int]:
    """Returns (max_score, query_idx, candidate_idx)."""
    sim = cosine_matrix(query_embs, candidate_embs)
    if sim.size == 0:
        return 0.0, -1, -1
    flat = np.argmax(sim)
    q, c = np.unravel_index(flat, sim.shape)
    return float(sim[q, c]), int(q), int(c)
