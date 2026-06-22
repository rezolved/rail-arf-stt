# Audio Dataset Curation Instructions

## Planning Guidelines

- Specify the audio source (production logs, rail-artifacts voice samples, or both) and the
  expected number of clips and total duration.
- List annotation requirements upfront: transcript format, entity span schema, utterance category
  tags (IR, ecommerce, other).
- Define the quality filter criteria (minimum clip length, acceptable SNR, speaker language) before
  starting collection.
- Estimate annotation cost: LLM-assisted transcription is cheap; manual review rounds are
  expensive. Budget time, not money, for this task type (`has_external_costs: false`).
- Plan the DVC tracking step explicitly — the audio directory must be added to DVC and pushed
  before the task PR is merged.

## Implementation Guidelines

- Always download audio clips to the task assets directory
  (`tasks/<task_id>/assets/dataset/<name>/files/`) and add a `.dvc` pointer file, not the raw
  bytes.
- Run `dvc push` after adding files so teammates can `dvc pull` them without contacting you.
- Annotation format must match `tasks/t0001_stt_benchmark/assets/dataset/stt-benchmark-gold-92/`
  as the reference schema (see `files/ground_truth.jsonl`).
- Never include gold-92 audio or transcripts in a training split — it is a held-out regression
  set only.
- Document dataset size, speaker demographics (if known), domain breakdown, and annotation
  methodology in the dataset asset `description.md`.

## Common Pitfalls

1. Forgetting `dvc push` before the PR — teammates get a pointer file that points to nothing.
2. Including gold-92 clips in a training or validation split — always cross-check clip IDs.
3. Inconsistent entity span schema between annotation rounds — lock the schema in the task plan
   before annotating.
4. Storing audio clips in git instead of DVC — pre-commit hooks will likely reject large files,
   but double-check.

## Related Skills

- `/implementation` — main execution skill
- `/research-code` — inspect existing annotation scripts in `brainpowa-realtime-api/scripts/evals/stt/`
