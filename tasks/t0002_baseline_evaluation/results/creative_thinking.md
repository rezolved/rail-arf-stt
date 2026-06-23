---
task_id: "t0002_baseline_evaluation"
step: "creative-thinking"
generated_at: "2026-06-23T10:10:00Z"
---
## Non-Obvious Findings and Analysis Angles

### 1. Entity accuracy is model-size invariant — the errors are systematic

Both Whisper turbo (809 M) and Whisper large-v3 (1.55 B) produce **identical entity accuracy:
25.2%** with identical 95% BCa CIs (18.1%–33.7%). WER differs (10.0% vs 10.6%) but entity accuracy
does not move at all. This rules out general transcription quality as the bottleneck. The entity
failures are **systematic vocabulary gaps** — domain terms like "Rezolve", "brainpowa", and
proprietary product names are simply absent from the model's training distribution. Scaling the
Whisper model does not help. The path to improvement is **vocabulary biasing** (initial_prompt,
PhraseListGrammar) or **post-correction**, not a bigger model.

### 2. Production clips are 4× worse than clean voices — the field gap is severe

Accent group breakdown for Whisper large-v3:

| Group | N clips | Entity accuracy |
| --- | --- | --- |
| clean_voices | 46 | **36.2%** |
| error_cases | 13 | **29.2%** |
| production | 34 | **8.8%** |

The production group (real investor-relations call recordings) achieves only 8.8% entity accuracy.
This is the actual production baseline — not 25.2%. The clean_voices number (36.2%) is inflated by
studio-quality recordings. Any roadmap metric should target **production clips only**.

### 3. Intent preservation (90.3%) is likely over-estimated by the proxy method

The current intent preservation measure is a span-presence heuristic: "intent is preserved if at
least one entity span from the reference appears in the hypothesis." This inflates the score
because:

* "Resolve" in the hypothesis satisfies the "Rezolve" entity check (normalised match).
* A user asking "Who is the CEO of Rezolve?" → hypothesis "Who is the CEO of Hizol?" scores 0 entity
  accuracy but the intent is still action-addressable (search for CEO of any company).

A proper intent classifier would distinguish: (a) entity substitution that changes action target vs.
(b) entity substitution that preserves action type. This is a future task.

### 4. Action-critical WER (30.4%) reveals where the domain gap actually hurts

General WER 10% looks acceptable. But action-critical WER 30.4% shows that **domain-specific
critical terms fail 3× more often** than general vocabulary. The critical-term subset contains
product names, company names, and commerce terms — exactly the entities that drive purchase actions.
Fixing these ~30% errors would close the gap between STT quality and business value.

### 5. Latency is entirely CPU-bound — streaming mode changes the picture

Both models run **well above the 800 ms p50 target** (4.25s turbo, 5.66s large-v3) on CPU-only M5.
However:

* These are **batch latencies** for complete-utterance transcription.
* In production streaming mode (`STT_STREAMING=true`), the first partial appears after the first
  re-transcription pass (~1 s of audio), giving TTFT well under 2 s.
* For the `<800 ms voice-to-action` target, the bottleneck is more likely the LLM call than STT.
* **Turbo is the pragmatic production choice**: 25% lower latency with no entity accuracy loss.

### 6. The "error_en" anomalies are a data quality signal worth investigating

The `error_*` prefix clips (annotation errors) score **29.2% entity accuracy** — better than
production. These clips likely have clearer audio despite annotation issues. Understanding what
makes production clips harder (compression artifacts, background noise, speaker overlap, domain
jargon density) should drive data collection for the next benchmark version.

### 7. Vocabulary-biased Whisper should be the next experiment

`STT_INITIAL_PROMPT` in brainpowa-realtime-api is the free-text vocabulary biasing channel for
Whisper. A prompt seeded with:
`"Rezolve, brainpowa, Rezolve AI, Shopify Plus, Salesforce Commerce Cloud, Adobe Commerce"` would
bias both models toward the correct entity forms at inference time — zero training required,
cost-free. This is the highest-ROI next step before any fine-tuning.
