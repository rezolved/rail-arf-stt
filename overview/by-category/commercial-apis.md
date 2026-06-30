# Category: Commercial APIs

Integration and evaluation of third-party STT APIs, primarily Deepgram Nova-2, as the
production baseline.

[Back to Dashboard](../README.md)

**Detail pages**: [Suggestions (4)](../suggestions/by-category/commercial-apis.md)

---

## Papers (0)

No papers in this category.

## Tasks (0)

No tasks related to this category.

## Answers (0)

No answers in this category.

## Suggestions (4 open, 0 closed)

<details>
<summary>🧪 <strong>Benchmark Granite Speech 4.1 2B vs Deepgram Nova-2 and Azure
Speech on gold-92 to complete the competitive landscape</strong>
(S-0014-05)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-30 | **Source**:
[t0014_granite_short_clip_robustness](../../tasks/t0014_granite_short_clip_robustness/)

Granite now leads all tested open-source models (EA 94.8%), but no direct comparison with
commercial APIs (Deepgram Nova-2, Azure Speech) has been run in production streaming mode with
the full domain biasing setup. S-0005-07 covers this but predates the t0012/t0014 findings
confirming Granite's edge. Running Granite against commercial APIs would determine whether
Granite already beats production Deepgram, answering the final commercial vs open-source
question. Recommended task types: stt-benchmark-run, answer-question.

</details>

<details>
<summary>🧪 <strong>Compare Granite/Paraformer against Deepgram Nova-2 and Azure
Speech on gold-92</strong> (S-0005-07)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-24 | **Source**:
[t0005_stt_model_survey_brainpowa](../../tasks/t0005_stt_model_survey_brainpowa/)

The survey did not include closed-API baselines (Deepgram Nova-2, Azure Speech Services). Both
support contextual biasing and have lower latency than Whisper. Run a comparative benchmark to
establish whether open-source candidates (Granite, Paraformer) can match or exceed the
accuracy and latency of production-quality closed APIs. This context is critical for
production decision-making if open-source candidates fall short. Azure Speech and Deepgram API
costs are approximately $0.01–$0.10 for 93 clips. Recommended task types: stt-benchmark-run,
comparative-analysis.

</details>

<details>
<summary>🧪 <strong>Run Deepgram Nova-2 baseline on gold-92 to complete REQ-1 and
paired significance test</strong> (S-0002-02)</summary>

**Kind**: experiment | **Priority**: high | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../../tasks/t0002_baseline_evaluation/)

The t0002 baseline evaluation could not run Deepgram Nova-2 because DEEPGRAM_API_KEY was
unavailable. This blocked REQ-1, REQ-5 (paired significance test), REQ-9 (Deepgram predictions
asset), and the production comparator column in all results tables. Cost is approximately
$0.09 for 93 clips. A dedicated task should obtain the key from the team vault, run Deepgram
Nova-2 with nova-2 model and default settings on all 93 gold-92 clips, compute all five
registered metrics with BCa CIs, run the paired significance test against whisper-turbo, and
produce the deepgram-nova2-gold92 predictions asset. Recommended task types:
stt-benchmark-run, baseline-evaluation.

</details>

<details>
<summary>🧪 <strong>Add Azure Speech Services as a third STT comparison point on
gold-92</strong> (S-0002-06)</summary>

**Kind**: experiment | **Priority**: medium | **Date**: 2026-06-23 | **Source**:
[t0002_baseline_evaluation](../../tasks/t0002_baseline_evaluation/)

Azure Cognitive Services Speech-to-Text supports custom keyword lists and phrase boosting
natively, making it a strong candidate for domain entity accuracy without fine-tuning. Compare
it against Deepgram Nova-2 and Whisper turbo on gold-92 using all five registered metrics.
Requires AZURE_SPEECH_API_KEY from the team vault. Azure also offers Custom Speech (domain
adaptation) which can be evaluated in a follow-up. Estimated cost: approximately $0.01–$0.05
for 93 clips at standard tier pricing. Recommended task types: stt-benchmark-run,
comparative-analysis.

</details>
