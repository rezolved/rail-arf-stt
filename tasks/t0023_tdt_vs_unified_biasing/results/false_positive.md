# t0023 — False Positive Test: verb 'resolve' → 'Rezolve'

**Clips:** 15 synthetic sentences, ground truth = verb 'to resolve'
**Model:** parakeet-unified-en-0.6b
**Boost params:** cs=3.0 ds=0.5 alpha=1.5

## Summary

| Config | False positives | Rate |
|--------|----------------|------|
| malsd NO boost | 0/15 | 0% |
| malsd WITH boost | 1/15 | 7% |

## Per-clip results

| File | Reference | No-boost hypothesis | Boost hypothesis | FP? |
|------|-----------|--------------------|-----------------|----|
| fp_0_.wav | we need to resolve this issue as quickly as possible |  | Adobe commerce. | no |
| fp_1_samantha.wav | can you help me resolve the problem with my order | Can you help me resolve the problem with my order | Can you help me resolve the problem with my order | no |
| fp_2_daniel.wav | i want to resolve the conflict before the meeting | I want to resolve the conflict before the meeting. | I want to resolve the conflict before the e-commerce. | no |
| fp_3_karen.wav | let me resolve that for you right away | Let me resolve that for you right away. | Let me resolve that for you right away. | no |
| fp_4_moira.wav | the team managed to resolve the dispute overnight | the team managed to resolve the dispute overnight. | the team managed to resolve the dispute overnight. | no |
| fp_5_.wav | please resolve the error in the payment system | I think it's not. | Adobe commerce. | no |
| fp_6_samantha.wav | we should resolve this matter immediately | We should resolve this matter immediately. | We should resolve this matter e-commercely. | no |
| fp_7_daniel.wav | i cannot resolve the issue without more information | I cannot resolve the issue without more information. | I cannot resolve the issue without more information. | no |
| fp_8_karen.wav | they failed to resolve the complaint in time | They failed to resolve the complaint in time | They failed to resolve the complaint in time | no |
| fp_9_moira.wav | how do you plan to resolve the situation | How do you plan to resolve the situation? | How do you plan to resolve the situation? | no |
| fp_10_.wav | the support team will resolve your ticket today | The support will resolve | The support will rezolve or | **YES** |
| fp_11_samantha.wav | we must resolve this before the deadline | We must resolve this before the deadline. | We must resolve this before the deadline. | no |
| fp_12_daniel.wav | i am trying to resolve the technical difficulty | I am trying to resolve the technical difficulty. | I am trying to resolve the technical difficulty. | no |
| fp_13_karen.wav | can we resolve the billing issue together | Can we resolve the billing issue together? | Can we resolve the billing issue together? | no |
| fp_14_moira.wav | the manager will resolve the concern promptly | The manager will resolve the concern promptly. | The manager will resolve the concern promptly. | no |

## Verdict

**Low risk.** 1/15 clips falsely transcribed as 'Rezolve'. Acceptable — only synthetic TTS, real speech risk may differ.
