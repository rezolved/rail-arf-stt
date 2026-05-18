import numpy as np
import pytest

from arf.scripts.stats.bootstrap_compare import (
    PairedDelta,
    SignFlipResult,
    Statistic,
    bca_paired_bootstrap_delta,
    sign_flip_permutation,
)

REGRESSION_BASELINE: list[float] = [
    1.0,
    2.0,
    3.0,
    4.0,
    5.0,
    6.0,
    7.0,
    8.0,
    9.0,
    10.0,
]
REGRESSION_CANDIDATE: list[float] = [
    1.6,
    2.4,
    3.7,
    4.3,
    5.8,
    6.2,
    7.9,
    8.1,
    9.6,
    10.4,
]
# Recorded historical values captured on first successful run with scipy 1.17.1,
# numpy 2.4.4, rng_seed=12345, n_resamples=5000. Treat these as the regression
# baseline: any later drift outside abs=1e-6 indicates a real change in BCa
# acceleration-constant computation that must be investigated.
REGRESSION_DELTA: float = 0.5
REGRESSION_LOWER: float = 0.3499999999999999
REGRESSION_UPPER: float = 0.6500000000000001
# Sign-flip with n=10 uses exact enumeration (2**10 = 1024 <= 10000).
REGRESSION_P_VALUE: float = 0.002926829268292683


def _make_nondegenerate_fixture() -> tuple[list[float], list[float]]:
    rng = np.random.default_rng(seed=42)
    baseline = [float(x) for x in rng.uniform(1.0, 5.0, size=30)]
    candidate = [b + float(rng.normal(0.5, 0.3)) for b in baseline]
    return baseline, candidate


def test_symmetry_mean() -> None:
    # Restricted to Statistic.MEAN: swap-negation is an exact identity only for
    # linear statistics. For percentiles the property requires an additional
    # symmetry assumption on the per-prompt distribution that we do not enforce.
    baseline, candidate = _make_nondegenerate_fixture()
    orig = bca_paired_bootstrap_delta(
        baseline,
        candidate,
        statistic=Statistic.MEAN,
        n_resamples=2000,
        rng_seed=99,
    )
    swapped = bca_paired_bootstrap_delta(
        candidate,
        baseline,
        statistic=Statistic.MEAN,
        n_resamples=2000,
        rng_seed=99,
    )
    assert swapped.delta == pytest.approx(-orig.delta, abs=1e-9)
    # Swap negates both bounds and reorders them: orig lower/upper become
    # -upper/-lower after swap.
    assert swapped.lower == pytest.approx(-orig.upper, abs=1e-9)
    assert swapped.upper == pytest.approx(-orig.lower, abs=1e-9)


def test_zero_effect() -> None:
    samples: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    pd = bca_paired_bootstrap_delta(
        samples,
        samples,
        statistic=Statistic.MEAN,
        n_resamples=1000,
        rng_seed=12345,
    )
    assert isinstance(pd, PairedDelta)
    assert pd.delta == 0.0
    # All-zero deltas trigger the BCa fallback to degenerate CI (lower==upper==point).
    assert pd.lower <= 0.0 <= pd.upper
    sf = sign_flip_permutation(
        samples,
        samples,
        statistic=Statistic.MEAN,
        n_permutations=1000,
        rng_seed=12345,
    )
    assert isinstance(sf, SignFlipResult)
    assert sf.observed_delta == 0.0
    assert sf.p_value == 1.0


def test_reproducibility() -> None:
    baseline, candidate = _make_nondegenerate_fixture()
    pd_a = bca_paired_bootstrap_delta(
        baseline,
        candidate,
        statistic=Statistic.MEAN,
        n_resamples=2000,
        rng_seed=12345,
    )
    pd_b = bca_paired_bootstrap_delta(
        baseline,
        candidate,
        statistic=Statistic.MEAN,
        n_resamples=2000,
        rng_seed=12345,
    )
    assert pd_a.delta == pytest.approx(pd_b.delta, rel=0, abs=0)
    assert pd_a.lower == pytest.approx(pd_b.lower, rel=0, abs=0)
    assert pd_a.upper == pytest.approx(pd_b.upper, rel=0, abs=0)
    sf_a = sign_flip_permutation(
        baseline,
        candidate,
        statistic=Statistic.MEAN,
        n_permutations=4000,
        rng_seed=12345,
    )
    sf_b = sign_flip_permutation(
        baseline,
        candidate,
        statistic=Statistic.MEAN,
        n_permutations=4000,
        rng_seed=12345,
    )
    assert sf_a.p_value == pytest.approx(sf_b.p_value, rel=0, abs=0)


def test_known_input_regression() -> None:
    pd = bca_paired_bootstrap_delta(
        REGRESSION_BASELINE,
        REGRESSION_CANDIDATE,
        statistic=Statistic.MEAN,
        n_resamples=5000,
        rng_seed=12345,
    )
    assert pd.delta == pytest.approx(REGRESSION_DELTA, abs=1e-9)
    assert pd.lower == pytest.approx(REGRESSION_LOWER, abs=1e-6)
    assert pd.upper == pytest.approx(REGRESSION_UPPER, abs=1e-6)
    sf = sign_flip_permutation(
        REGRESSION_BASELINE,
        REGRESSION_CANDIDATE,
        statistic=Statistic.MEAN,
        n_permutations=10000,
        rng_seed=12345,
    )
    # n=10 pairs => 2**10 = 1024 <= 10000, so exact enumeration is used.
    assert sf.exact is True
    assert sf.n_permutations_used == 1024
    assert sf.p_value == pytest.approx(REGRESSION_P_VALUE, abs=1e-9)


def test_ci_ordering() -> None:
    baseline, candidate = _make_nondegenerate_fixture()
    for stat in Statistic:
        pd = bca_paired_bootstrap_delta(
            baseline,
            candidate,
            statistic=stat,
            n_resamples=2000,
            rng_seed=99,
        )
        assert pd.lower <= pd.delta <= pd.upper, (
            f"CI ordering violated for {stat}: lower={pd.lower} delta={pd.delta} upper={pd.upper}"
        )
