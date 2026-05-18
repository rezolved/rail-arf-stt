# Warmup-N + Measured-M Protocol

**Version**: 1

## Goal

Force every latency benchmark in a Rezolve research project to issue a fixed warmup phase before
the measured phase, on the same engine session, with the warmup records discarded. This makes
results comparable across tasks and projects, and prevents cold-cache contamination of cold-vs-warm
deltas (see `LESSONS.md`, Lesson 1).

## Protocol

1. Open one client / engine session.
2. Send `DEFAULT_WARMUP_N` (default 50) prompts from a corpus. Stream the responses to completion;
   do **not** persist any per-request metrics. Failed warmup requests are tolerated but counted.
3. On the **same session**, send `DEFAULT_MEASURED_N` (default 20) prompts. Persist one record per
   prompt with at minimum: `request_id`, `prompt_index`, `start_time`, `end_time`, `ttft_seconds`,
   `latency_seconds`, `status`, `provider_label`.
4. Write a `latency_benchmark_run` asset (see
   `meta/asset_types/latency_benchmark_run/specification.md`) containing:

   * The measured records.
   * `details.warmup_requests` (the actual warmup count run).
   * `details.warmup_corpus_ref` (a stable reference to the warmup corpus — task-defined).
   * Infrastructure-version fields (`engine_version`, `cuda_version`, `cudnn_version`,
     `container_image_sha`) captured at benchmark time.

## What this package ships

* `constants.py` — protocol defaults (`DEFAULT_WARMUP_N=50`, `DEFAULT_MEASURED_N=20`), status
  strings, asset-spec-version constant.
* `__init__.py` — re-exports the constants.

## What this package does NOT ship

The on-VM streaming runner that actually issues HTTP requests against the engine. That code is
necessarily engine-specific (vLLM OpenAI streaming, SGLang, TRT-LLM, Triton, etc.) and lives in the
task that uses it. Two reference implementations to copy from:

* `rezolved/rail-arf-serving` `tasks/t0013_warmup_protocol_and_t0004_anchor_correction/code/` —
  the original promotion task. Uses the t0010 latency harness against vLLM's
  `/v1/chat/completions` streaming endpoint.
* `rezolved/rail-arf-serving` `tasks/t0021_engine_head_to_head_sglang_trtllm/code/vm_run_warmup_measure.py`
  — adapted on-VM runner that drops to raw streaming for non-OpenAI-compatible engines.

## Verification

A task using this protocol must pass `verify_latency_benchmark_run_warmup` — it inspects every
`latency_benchmark_run` asset under `tasks/<task_id>/assets/` and warns if `warmup_requests` is
absent or zero, or if `warmup_corpus_ref` is null.

```bash
uv run python -u -m arf.scripts.verificators.verify_latency_benchmark_run_warmup <task_id>
```
