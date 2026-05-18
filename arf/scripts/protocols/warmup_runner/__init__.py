"""Warmup-N + measured-M paired protocol library.

This package ships the protocol *shape* and constants for paired latency
benchmarks. The engine-specific runner that issues actual streaming requests
must be supplied by the task — see
`arf/scripts/protocols/warmup_runner/README.md` for the protocol contract
and `LESSONS.md` (Lesson 1: cold vs. warm cache) for the rationale.

Public surface:

* `DEFAULT_WARMUP_N`, `DEFAULT_MEASURED_N` — protocol defaults (50, 20).
* `LATENCY_BENCHMARK_RUN_SPEC_VERSION` — asset spec version that any task
  conforming to this protocol must declare in `details.json`.
"""

from arf.scripts.protocols.warmup_runner.constants import (
    DEFAULT_MEASURED_N,
    DEFAULT_NOTE,
    DEFAULT_WARMUP_N,
    ENDPOINT_KIND_EXTERNAL_PROVIDER,
    ENDPOINT_KIND_LOCAL,
    LATENCY_BENCHMARK_RUN_SPEC_VERSION,
    PROVIDER_LABEL_DEFAULT,
    STATUS_FAILURE,
    STATUS_SUCCESS,
)

__all__ = [
    "DEFAULT_MEASURED_N",
    "DEFAULT_NOTE",
    "DEFAULT_WARMUP_N",
    "ENDPOINT_KIND_EXTERNAL_PROVIDER",
    "ENDPOINT_KIND_LOCAL",
    "LATENCY_BENCHMARK_RUN_SPEC_VERSION",
    "PROVIDER_LABEL_DEFAULT",
    "STATUS_FAILURE",
    "STATUS_SUCCESS",
]
