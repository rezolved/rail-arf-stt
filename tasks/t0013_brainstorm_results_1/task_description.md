# t0013 — Brainstorm Results: Session 1

## Overview

First brainstorm session for the rail-arf-stt project. Reviewed all 12 completed tasks, assessed the
24 active suggestions, and decided on one new task and six suggestion rejections.

## Context

All 12 tasks completed. The model landscape is clear: Whisper turbo (42.0% EA) and Granite Speech
4.1 2B (41.1% EA) lead by a large margin over the current production model Parakeet TDT 0.6b-v3
(23.2% EA). Nemotron, Moonshine, and FunASR Paraformer are eliminated. The strategic question is
whether Granite can replace Parakeet in production — complicated by a known Whisper failure mode on
short audio clips that was the original reason Parakeet was adopted.

## Decisions

1. Create t0014: Granite short-clip robustness validation and production fit assessment. Simulates
   real production streaming (32kB PCM-16 chunk queue via `transcribe_stream()`) on synthetic short
   clips (0.5–2s) and stratified gold-92 analysis. GPU run on Azure H100 NVL.
2. Reject S-0002-01: superseded by t0004.
3. Reject S-0005-04: Moonshine eliminated.
4. Reject S-0005-09: FunASR Paraformer eliminated.
5. Reject S-0008-01: Moonshine eliminated.
6. Reject S-0008-02: Moonshine eliminated.
7. Reject S-0008-03: Moonshine eliminated.
