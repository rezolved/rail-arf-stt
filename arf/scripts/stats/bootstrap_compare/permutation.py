import itertools
from dataclasses import dataclass

import numpy as np

from arf.scripts.stats.bootstrap_compare.bca import (
    _statistic_fn,
)
from arf.scripts.stats.bootstrap_compare.constants import (
    BOOTSTRAP_SEED,
    PERMUTATION_ITERATIONS,
    Statistic,
)


@dataclass(frozen=True, slots=True)
class SignFlipResult:
    statistic: Statistic
    observed_delta: float
    p_value: float
    n_pairs: int
    n_permutations_used: int
    exact: bool


def sign_flip_permutation(
    baseline_per_prompt: list[float],
    candidate_per_prompt: list[float],
    *,
    statistic: Statistic,
    n_permutations: int = PERMUTATION_ITERATIONS,
    rng_seed: int = BOOTSTRAP_SEED,
) -> SignFlipResult:
    assert len(baseline_per_prompt) == len(candidate_per_prompt), (
        "baseline and candidate arrays must have equal length"
    )
    assert len(baseline_per_prompt) > 0, "input arrays must be non-empty"

    arr_baseline = np.asarray(baseline_per_prompt, dtype=float)
    arr_candidate = np.asarray(candidate_per_prompt, dtype=float)
    # Sign convention: positive Δ = candidate slower than baseline.
    deltas = arr_candidate - arr_baseline
    n_pairs = int(deltas.size)
    stat_fn = _statistic_fn(statistic)
    observed = float(stat_fn(deltas, -1))

    if observed == 0.0:
        return SignFlipResult(
            statistic=statistic,
            observed_delta=observed,
            p_value=1.0,
            n_pairs=n_pairs,
            n_permutations_used=0,
            exact=False,
        )

    use_exact = (2**n_pairs) <= n_permutations
    if use_exact:
        signs = np.array(
            list(itertools.product([-1.0, 1.0], repeat=n_pairs)),
            dtype=float,
        )
        n_total = int(signs.shape[0])
    else:
        rng = np.random.default_rng(seed=rng_seed)
        signs = rng.choice(a=np.array([-1.0, 1.0]), size=(n_permutations, n_pairs))
        n_total = n_permutations

    perm_arr = signs * deltas
    perm_stats = stat_fn(perm_arr, -1)
    count_ge = int(np.sum(np.abs(perm_stats) >= abs(observed)))
    # +1/+1 finite-sample correction so p is never exactly zero.
    p_value = float((count_ge + 1) / (n_total + 1))

    return SignFlipResult(
        statistic=statistic,
        observed_delta=observed,
        p_value=p_value,
        n_pairs=n_pairs,
        n_permutations_used=n_total,
        exact=use_exact,
    )
