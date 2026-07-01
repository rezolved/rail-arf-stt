# Project Costs

Spent $290.08 of $2000.00 USD. $1709.92 remains overall and $1709.92 remains before the 100%
stop threshold.

## Budget Summary

| Field | Value |
|-------|-------|
| Total budget | $2000.00 USD |
| Total spent | $290.08 USD |
| Budget left | $1709.92 USD |
| Budget left before stop threshold | $1709.92 USD |
| Spent percent | 14.50% |
| Warn threshold | 80% ($1600.00) |
| Stop threshold | 100% ($2000.00) |
| Default per-task limit | $100.00 USD |
| Tasks with cost records | 8 |
| Tasks with non-zero spend | 2 |
| Skipped tasks | 8 |

## Service Totals

| Key | Cost (USD) |
|-----|------------|
| `azure_ml` | $287.58 |
| `anthropic_api` | $2.50 |

## Breakdown Totals

| Key | Cost (USD) |
|-----|------------|
| `azure-ml-2xh100` | $287.58 |
| `claude-code-orchestration` | $2.50 |

6 task cost record(s) are zero-cost and omitted from the main spend table.

## Task Spend

| Task | Status | Total (USD) | Limit (USD) | Over limit |
|------|--------|-------------|-------------|------------|
| [`t0002_baseline_evaluation`](../../overview/tasks/task_pages/t0002_baseline_evaluation.md) | completed | $2.50 | $100.00 | no |
| [`t0015_streaming_buffer_interval`](../../overview/tasks/task_pages/t0015_streaming_buffer_interval.md) | completed | $287.58 | $100.00 | yes |

## Skipped Tasks

| Task ID | Reason |
|---------|--------|
| `t0001_stt_benchmark` | results/costs.json missing a numeric total_cost_usd |
| `t0006_nemotron_3_5_benchmark` | results/costs.json is missing or invalid |
| `t0007_ibm_granite_4_1_benchmark` | results/costs.json is missing or invalid |
| `t0009_parakeet_production_baseline` | results/costs.json is missing or invalid |
| `t0010_funasr_paraformer_benchmark` | results/costs.json is missing or invalid |
| `t0011_streaming_stt_benchmark` | results/costs.json is missing or invalid |
| `t0012_whisper_parakeet_granite_streaming` | results/costs.json is missing or invalid |
| `t0016_streaming_fuzzy_hotword_correction` | results/costs.json is missing or invalid |
