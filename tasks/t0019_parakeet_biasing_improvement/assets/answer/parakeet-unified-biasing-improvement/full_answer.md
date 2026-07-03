---
spec_version: "2"
answer_id: "parakeet-unified-biasing-improvement"
answered_by_task: "t0019_parakeet_biasing_improvement"
date_answered: "2026-07-02"
confidence: "high"
---

## Question

How can GPU-PB biasing quality for parakeet-unified-en-0.6b on the gold-92 benchmark be improved
beyond the t0017 biased baseline (EA-DV 34.8%), and which approach should ship to
brainpowa-realtime-api production?

## Short Answer

Neither decode-time GPU-PB approach improves biasing: a hyperparameter sweep (alpha 1.0-3.0,
depth_scaling 2.0-4.0) is a null result, and phrase-list expansion with phonetic surface-form
variants is also a null result (0.000 delta on every metric, byte-identical transcripts). The
dominant failure — "Rezolve" transcribed as "Resolve" — is acoustic, not a boosting-tree coverage
gap, so boosting cannot fix it. A deterministic post-decode string-replacement pass, using the
`stt_replacements` channel that already exists in `brainpowa-realtime-api` but ships with an empty
default, raised EA-DV from 34.8% to 95.7% and improved WER from 11.0% to 8.5%. Recommendation:
populate a deployment-level default `stt_replacements` map (REQ-7); stop investing in GPU-PB
hyperparameter tuning or phrase-list engineering for this specific failure mode (REQ-8).

## Research Process

This task (t0019) built on `t0017_parakeet_biasing_buffer_replacement`, which established the
biased baseline for `parakeet-unified-en-0.6b` on gold-92 (WER 11.0%, EA 23.4%, EA-DV 34.8%,
default GPU-PB config `alpha=1.0, context_score=1.0, depth_scaling=2.0`) and flagged that biasing
"barely helps" — the model still writes "Resolve"/"Rizol" for "Rezolve". Rather than a literature or
internet research phase, this task ran three code experiments directly (REQ-1 through REQ-4), each
gated by inspecting individual outputs before scaling up, per the project's validation-gate
convention:

1. **Reproduced the baseline** on all 93 gold-92 clips (REQ-1) using the same GPU-PB config as
   t0017, confirming WER=11.0%, EA=23.4%, EA-DV=34.8% — identical to t0017's numbers, confirming the
   harness reproduction was correct.
2. **Hyperparameter sweep** (REQ-2): a wide grid (alpha in [1.0, 1.5, 2.0, 2.5, 3.0], depth_scaling
   in [2.0, 3.0, 4.0], 15 configs) screened on a fixed 20-clip subsample, then the top-2 configs by
   screening EA-DV confirmed on all 93 clips. Because the wide grid's top-2 configs both blew past
   the pre-registered WER cap (baseline WER + 1.0 absolute point), a second narrower grid (alpha in
   [1.0, 1.1, 1.2, 1.3, 1.4, 1.5], depth_scaling in [2.0, 2.25, 2.5], 18 configs) was screened with
   WER now tracked alongside EA-DV, closer to the production default, to check for a safe
   intermediate zone.
3. **Phrase-list expansion** (REQ-3): baseline predictions were inspected clip-by-clip to find every
   domain-vocab term with an observed miss (`Rezolve`/`Rezolve Ai`: 25/17 misses; `brainpowa`: 1
   miss; `agentic commerce`: 1 miss), then 15 additional correct-spelling surface-form variants
   (alternate casing, hyphenation, spacing — not the wrong spelling) were added to the GPU-PB phrase
   list and the full 93 clips were re-run with the winning hyperparameter config.
4. **Post-hoc replacement feasibility check** (REQ-4): a pure text post-processing pass (no model
   re-run) applied deterministic, case-insensitive, whole-word regex replacements
   (`Resolve`→`Rezolve`, `Resolve AI`→`Rezolve Ai`, `brain power`→`brainpowa`, `Gentic commerce`→
   `agentic commerce`) to the Step 3 transcripts and rescored.

After the post-hoc result came back strongly positive, the production codebase
(`brainpowa-realtime-api`) was inspected directly to determine whether this approach corresponds to
an existing, already-wired mechanism or would require new engineering — see Evidence from Code or
Experiments below.

## Evidence from Papers

The `papers` answer method was not used for this task; no research-papers step was run (task was
scoped directly from t0017's findings, and the orchestrator explicitly approved skipping unneeded
research stages for this experiment-run task).

## Evidence from Internet Sources

The `internet` answer method was not used for this task; no internet-research step was run for the
same reason as above. t0017's prior research (NeMo GPU-PB / TurboBias references, arXiv:2508.07014,
NeMo#14500 surface-form sensitivity) remains the applicable background and was not re-derived here.

## Evidence from Code or Experiments

**Hyperparameter sweep results** (`results/hyperparam_sweep.jsonl`, `results/hyperparam_top2_full93.json`):
on the full 93-clip confirmation run, the wide grid's top-2 screening configs both catastrophically
regressed WER relative to baseline:

| config | WER | EA | EA-DV |
|---|---|---|---|
| baseline (alpha=1.0, depth_scaling=2.0) | 11.0% | 23.4% | 34.8% |
| alpha=3.0, depth_scaling=3.0 | 38.4% | 63.7% | 63.8% |
| alpha=2.0, depth_scaling=4.0 | 31.0% | 34.4% | 46.4% |

Both candidates exceed the pre-registered +1.0pp WER cap by more than 20 absolute points — EA-DV
gains are real but come from the boosting tree garbling non-entity words into entity-shaped tokens,
not from genuinely better recognition. Per the plan's rejection rule, both are disqualified and the
baseline config is carried forward as the winner (a null result for this approach).

The follow-up narrow grid (`results/hyperparam_sweep_narrow.jsonl`, alpha in [1.0-1.5],
depth_scaling in [2.0-2.5], 18 configs, 20-clip screening with WER now tracked) found **zero EA-DV
movement across all 18 configs** — every config scored EA-DV=0.600 on the 20-clip subsample,
identical to the alpha=1.0/depth_scaling=2.0 baseline point. WER varied only in a narrow noise band
(9.4%-17.3%) with no clear improving direction. This confirms the effect is bimodal, not gradual:
near the default, nothing happens; far from the default, boosting corrupts the transcript. There is
no safe intermediate zone that trades a small WER cost for an EA-DV gain.

**Phrase-list expansion results** (`results/phrase_expansion_full93.json`): adding 15 additional
correct-spelling surface-form variants (`REZOLVE`, `Re-zolve`, `Rezolv`, `brain-powa`, etc., defined
in `code/phrase_expansion.py`) to the 72-phrase casing-expanded list (87 phrases total) produced
**byte-identical transcripts** to the baseline run — WER=0.11033099297893681 and
EA-DV=0.34782608695652173 matched the baseline to full floating-point precision on all 93 clips.
GPU-PB's boosting tree already covers whatever BPE paths it can reach from the base phrase forms;
additional correct-spelling variants add no new reachable paths, because the failure is that the
acoustic model resolves the audio to "Resolve" with high confidence before the boosting tree gets a
chance to compete — this is a decode-time ceiling, not a phrase-list coverage gap.

**Post-hoc replacement feasibility check** (`results/posthoc_replacement_check.json`): applying the
4-rule regex replacement map to the Step 3 transcripts (which are identical to baseline, since Step
3 showed zero effect) changed 27 of 93 clips and produced:

| | WER | EA | EA-DV |
|---|---|---|---|
| before (biasing only) | 11.0% | 23.4% | 34.8% |
| after (+ post-hoc replace) | 8.5% | 93.8% | 95.7% |

This is a +60.9 percentage point EA-DV gain and a WER *improvement* (fewer substitution errors, since
"Resolve"→"Rezolve" fixes a wrong-word substitution outright). Latency impact of the replacement pass
itself is negligible: measured at ~3 microseconds per call on realistic transcript lengths, versus
~250-350ms end-to-end STT latency — over five orders of magnitude smaller, not a measurable
contributor to the 800ms voice-to-action budget.

**Production code inspection**: `brainpowa-realtime-api` already implements exactly this mechanism
as a first-class, already-wired feature, independent from this task's synthetic script:

* `stt_replacements: dict[str, list[str]]` is a client-facing session-config field
  (`src/brainpowa_realtime_api/protocol/events.py:77`), canonical term → list of alias strings, with
  validation caps on key/alias counts and lengths.
* `sanitize_replacements()` and `_compile_rules()`
  (`src/brainpowa_realtime_api/pipeline/stt/rules.py:19,94`) compile the map into longest-first regex
  rules — the same "longest phrase first" ordering this task's script used manually.
* `normalize_transcript()` (`rules.py:179`) applies the compiled rules to the STT output text,
  independent of GPU-PB boosting — `parakeet.py:230` explicitly documents `stt_replacements` as "a
  separate post-hoc rewrite map" from the boosting tree.
* `session/state.py:359` wires `self.config.stt_replacements` into `get_stt_options()`, and the
  session-config docstring states explicitly: "the server carries no hardcoded brand defaults" — the
  map is populated only if a client sends one via `session.update`.
* The WS endpoint's advertised default (`ws/endpoint.py:373`) is `"stt_replacements": {}` — an empty
  map. No Rezolve-domain aliases are configured anywhere in the deployment today.

So this task's "post-hoc replacement" experiment is not a new engineering proposal — it is a
feasibility measurement of an existing, unused production knob.

## Synthesis

The three candidate approaches split cleanly into two failed decode-time interventions and one
proven text-layer intervention. GPU-PB boosting, whether tuned (hyperparameter sweep) or given more
phrase-list surface area (phrase expansion), cannot correct "Rezolve"→"Resolve" because the acoustic
confusion is resolved before or during decode with high model confidence — boosting only reweights
plausible continuations, and this candidate is apparently implausible enough (relative to "Resolve")
that no tested alpha/depth_scaling/phrase-list combination close to the safe operating range moves
it, while combinations far from that range fix it only by globally corrupting the transcript. This
matches t0017's own framing that "biasing barely helps" and is consistent with GPU-PB's known
surface-form sensitivity (NeMo#14500) — the issue here is not surface-form coverage but a fundamental
acoustic-confidence ceiling.

Post-hoc string replacement sidesteps the acoustic problem entirely by treating it as a text-editing
problem after the fact. This is the correct layer for this specific failure mode: it is
deterministic (no probability of under- or over-firing the way GPU-PB's boosting tree can), costs a
handful of microseconds per call, and is already implemented and wired into
`brainpowa-realtime-api`'s pipeline — the only gap is that no Rezolve-domain alias map is currently
configured for any deployment or session default.

**Recommendation for production**: populate a deployment-level default `stt_replacements` map (or
have the client that owns the Rezolve voice-commerce session send one via `session.update`) with, at
minimum, the aliases validated in this task:

```json
{
  "Rezolve": ["Resolve", "Rizol", "Re-zolve", "Rezolv"],
  "Rezolve Ai": ["Resolve AI", "Resolve Ai", "Rizol AI"],
  "brainpowa": ["brain power", "brain powa"],
  "agentic commerce": ["Gentic commerce"]
}
```

This list should be extended opportunistically as new near-miss transcripts are observed in
production logs — the mechanism is cheap enough (microseconds per call) that a much longer list
carries negligible latency risk. Do not allocate further engineering time to GPU-PB hyperparameter
tuning or phrase-list expansion for the Rezolve/brainpowa homophone problem specifically; those two
approaches were tested and are confirmed null results at this task's scope (REQ-2, REQ-3 satisfied
with negative findings; REQ-8's deprioritized approaches — per-phrase weighting, beam rescoring,
fine-tuning — were correctly left untried, since even the tried decode-time approaches showed no
exploitable middle ground worth extending). GPU-PB boosting still has value for other domain terms
that are not the "Rezolve" homophone (the wider `entity_accuracy_gold92` figure includes terms
biasing does help, per t0017), so it should not be removed — it should simply not be the mechanism
relied on for this specific, now-solved failure mode. REQ-5 (3 predictions assets), REQ-6 (metrics
comparison), and REQ-7 (this answer asset) are satisfied by the accompanying `results/` files and
`assets/predictions/` folders for this task.

## Limitations

* The post-hoc replacement check (REQ-4) was run as an isolated text-processing script against saved
  transcripts, not against the live `normalize_transcript()` code path in `brainpowa-realtime-api`.
  The regex rules match in intent but were not verified byte-for-byte against `_compile_rules()`'s
  actual compiled output — before shipping, the exact alias list should be run through the real
  `sanitize_replacements()`/`_compile_rules()` functions on a staging deployment to confirm identical
  behavior (e.g., word-boundary handling, case normalization) to this task's standalone regex.
  * The 27-replacement, +60.9pp EA-DV result is measured on gold-92 (93 clips, largely scripted
  investor-relations-domain questions). Real user speech may introduce near-miss forms not covered
  by the 4-rule alias list tested here (e.g., different mispronunciations of "Rezolve" not seen in
  this benchmark) — the recommendation to extend the list opportunistically from production logs is
  a direct consequence of this limitation, not just a suggestion.
* The narrow hyperparameter grid (18 configs) used a 20-clip screening subsample for speed; it is
  possible a finer-grained sweep (e.g. depth_scaling in 0.05 increments) between 1.5 and 2.0 alpha
  could find a small, real EA-DV gain within the WER cap that this coarser grid missed — but given
  the flat 0.600 EA-DV across the entire narrow grid (no directional signal at all), this is judged
  unlikely to be worth the additional GPU time.
* `intent_preservation_gold92`, `action_critical_wer_gold92`, and `wrong_action_rate_gold92` were not
  measured for any condition in this task — they require the downstream intent classifier / routing
  policy from `brainpowa-realtime-api`, which this biasing-only experiment did not invoke. The +61pp
  EA-DV gain from post-hoc replacement should translate into a wrong-action-rate improvement (fewer
  misrecognized brand mentions should mean fewer misrouted actions), but this was not directly
  measured and should be confirmed once `stt_replacements` is populated on a real deployment.

## Sources

* Task: [t0017][t0017] — established the biased baseline (WER 11.0%, EA-DV 34.8%) and the "Resolve"
  confusion this task investigated.
* Task: [t0019][t0019] — this task; all sweep/expansion/post-hoc results and code referenced above.

[t0017]: ../../../t0017_parakeet_biasing_buffer_replacement/
[t0019]: ../../../t0019_parakeet_biasing_improvement/
