DEFAULT_WARMUP_N: int = 50
DEFAULT_MEASURED_N: int = 20

PROVIDER_LABEL_DEFAULT: str = "<set-per-task>"
ENDPOINT_KIND_LOCAL: str = "local_engine_config"
ENDPOINT_KIND_EXTERNAL_PROVIDER: str = "external_provider"

DEFAULT_NOTE: str = (
    "Warmup-N + measured-M paired protocol. Warmup records are discarded; "
    "only measured records are persisted."
)

LATENCY_BENCHMARK_RUN_SPEC_VERSION: str = "1"
STATUS_SUCCESS: str = "success"
STATUS_FAILURE: str = "failure"
