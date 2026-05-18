from enum import Enum


class Statistic(Enum):
    MEAN = "mean"
    P50 = "p50"
    P95 = "p95"
    P99 = "p99"


BOOTSTRAP_SEED: int = 12345
BOOTSTRAP_ITERATIONS: int = 5000
PERMUTATION_ITERATIONS: int = 10000
CONFIDENCE_LEVEL: float = 0.95
