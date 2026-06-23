---
task_id: "t0003_literature_review_entity_stt"
date: "2026-06-23"
total_queries: 14
---
# Search Log — Literature Review: Entity-Aware STT for Ecommerce Voice AI (Jan–Jun 2026)

All 14 queries were executed during the research phase. Queries 1–6 are the required keyword
combinations from `task_description.md`. Queries 7–14 are gap-filling and snowball queries run to
address gaps identified after initial results. Date of all searches: 2026-06-23.

## Required Keyword Combinations

| # | Query | Databases | Result Count | Papers Selected |
| --- | --- | --- | --- | --- |
| 1 | `contextual biasing ASR named entity 2026` | arXiv cs.CL, Semantic Scholar, Papers With Code | ~25 results | Ren2026 (`10.48550_arXiv.2601.13409`), Huang2026 (`10.48550_arXiv.2603.25460`), Novitasari2026 (`10.48550_arXiv.2604.12398`), Tsai2026 (`10.48550_arXiv.2605.18222`); background: Gong2025/BR-ASR, Sudo2025/OWSM-Biasing |
| 2 | `entity-aware speech recognition ecommerce 2026` | arXiv cs.CL, Semantic Scholar, ACL Anthology | ~18 results | Durmus2026 (`10.48550_arXiv.2604.07354`), Jiang2026 (`10.48550_arXiv.2605.29430`) |
| 3 | `shallow fusion ASR latency 2026` | arXiv cs.CL/cs.SD, Semantic Scholar, ICASSP 2026 | ~8 results | **0 primary papers** (no standalone shallow fusion paper in Jan–Jun 2026); background: Hori2025/Delayed Fusion (ICASSP 2025) |
| 4 | `LLM post-correction ASR named entity 2026` | arXiv cs.CL, Semantic Scholar | ~30 results | Ron2026 (`10.48550_arXiv.2602.18966`), Kumar2026/RECOVER (`10.48550_arXiv.2603.16411`), Zheng2026 (`10.48550_arXiv.2601.21347`), An2026/RASTAR (`10.48550_arXiv.2602.12287`), Poncelet2026 (`10.48550_arXiv.2606.10838`) |
| 5 | `domain-specific ASR brand product 2026` | arXiv cs.CL/eess.AS, Semantic Scholar, Emergent Mind | ~15 results | Tay2026/WildASR (`10.48550_arXiv.2603.25727`); confirmed Durmus2026 and Jiang2026 |
| 6 | `Whisper fine-tuning named entity ecommerce 2026` | arXiv cs.CL, Semantic Scholar, Google web search | ~12 results | Ron2026 (confirmed as most directly applicable Whisper-specific technique); Kudlur2026/Moonshine v2 (`10.48550_arXiv.2602.12241`) discovered via latency-related results |

## Gap-Filling Queries

| # | Query | Databases | Result Count | Papers Selected |
| --- | --- | --- | --- | --- |
| 7 | `arXiv cs.CL entity-aware ASR contextual biasing 2026 new papers` | arXiv cs.CL browse (Jan–Jun 2026) | ~40 browsed | Wang2026/LOGIC (`10.48550_arXiv.2601.15397`); confirmed An2026, Kudlur2026 |
| 8 | `ICASSP 2026 proceedings speech recognition entity accuracy` | ICASSP 2026 program search | ~20 results | No primary additions; confirmed no standalone shallow fusion papers at ICASSP 2026 |
| 9 | `Interspeech 2026 contextual biasing named entity speech` | Interspeech 2026 program search | ~15 results | Kumar2026/RECOVER confirmed as Interspeech 2026; LOGIC monitoring flag set |
| 10 | `accented English ASR named entity recognition voice AI 2026` | arXiv, Semantic Scholar, Google web search | ~10 results | Tay2026/WildASR confirmed as most relevant (accent evaluation methodology); no entity-level accent paper found |
| 11 | `ecommerce voice assistant benchmark dataset ASR entity WER 2026` | arXiv, ACL Anthology, Semantic Scholar | ~8 results | **0 primary ecommerce-specific papers**; gap confirmed |
| 12 | `Contextual Earnings-22 benchmark custom vocabulary contextual biasing ASR evaluation 2026` | arXiv, ADS (NASA), Google web search | 1 direct result | Durmus2026 (`10.48550_arXiv.2604.07354`) confirmed and asset created |
| 13 | `TARQ tail-aware quantization rare word robust ASR 2026 arxiv entity` | arXiv cs.SD/eess.AS, Semantic Scholar | 1 direct result | Wang2026b/TARQ (`10.48550_arXiv.2605.27808`) confirmed and asset created |
| 14 | `speculative decoding LLM ASR post-correction latency 2026 arxiv` | arXiv cs.CL, Semantic Scholar | ~12 results | No additional primary papers; confirmed Jiang2026 and Ron2026 as the latency-relevant post-correction papers in scope |

## Summary

* **Total queries**: 14
* **Queries with primary paper additions**: 9 of 14
* **Queries with zero primary additions**: 5 (queries 3, 8, 10, 11, 14)
* **Confirmed literature gap**: shallow fusion (query 3) — no standalone 2026 paper
* **Confirmed literature gap**: ecommerce-specific benchmark (query 11) — no 2026 paper
* **Primary assets created**: 15 total (11 from queries 1, 2, 4, 5, 6, 7; 4 from gap-filling queries
  12–13 and internet discovery: Durmus2026, Wang2026/LOGIC, Wang2026b/TARQ, Tay2026/WildASR)
* **Background papers noted**: 7 (Gong2025/BR-ASR, Hori2025/Delayed Fusion, Trinh2025,
  Sudo2025/OWSM-Biasing, WhisperNER, Im2025/DeRAGEC, Altinok2025)

## Notes on Reconstruction

Query result counts are approximate. The arXiv browse (query 7) was a manual scan of cs.CL new
submissions for January–June 2026 rather than a keyword search with a discrete result count; the
count of "~40 browsed" reflects the number of titles inspected before selecting additions. All other
result counts are from keyword search results and are accurate to ±2.
