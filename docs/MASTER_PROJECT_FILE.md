# MASTER PROJECT FILE (Complete, Standalone Reference)
## "Preserving Dialects, Enhancing Communication: A Model For Translating Regional Bangladeshi Languages into Standard Bengali"

**Purpose of this document:** This is a complete, self-contained technical and narrative record of this research
project, from the very first data-collection decision through to the final, locked model results. It is written
so that **another AI assistant, with no other files or context, could use this document alone to (a) understand
everything that has been done, (b) help finish the thesis report, and (c) help build the web interface, and even
(c2) regenerate the exact same training pipeline from scratch if the original notebooks were lost.**

If anything below references a file that may not be available in a new session, the exact information needed to
recreate that file's function is also written out in full below -- the file is a convenience, not a dependency.

---

# PART A -- PROJECT SCOPE

## A.1 Final, Locked Scope

- **Direction: single-direction only -- Dialect to Standard Bengali.** A bidirectional (Dialect <-> Standard)
  version and a "hybrid model" (region-routing ensemble) were both explored as ideas during development but were
  **deliberately dropped** to match the officially registered thesis title (above) and to fit the project
  deadline. Do not build or describe a bidirectional or hybrid system -- the delivered system translates dialect
  input into Standard Bengali only.
- **Seven regional dialects covered:** Pabna, Noakhali, Jashore, Rangpur, Mymensingh, Barishal, Chittagong.
- **Final selected model: BanglaT5** (`csebuetnlp/banglat5`, fine-tuned). It outperformed mT5-base and mT5-small
  on every metric (see Part D for full results). mT5-base and mT5-small were kept as **comparison-only** models
  for a Results-chapter ablation table, not as candidates for the deployed system.
- **Report chapters already drafted separately by the student:** Chapters 1, 2, 3 (partial -- see Part F), and 5,
  in a file called `Before_formating_report.docx`. **This file has not yet been reviewed in detail in this
  conversation** -- if picking up report-editing work, ask the student to upload it again and review it before
  editing, rather than assuming its contents.
- **Two remaining tasks the student needs help with right now:** (1) finishing/polishing the thesis report, and
  (2) building a web interface for the finished model. Both are covered in Parts F and G below.

---

# PART B -- DATASET

## B.1 Structure

**Source file:** `Master_sheet_Dataset.xlsx` -- 2,500 rows. Columns: `ID`, `Standard Bangla`, `Banglish`,
`English`, and one column per region (`Pabna`, `Noakhali`, `Jashore`, `Rangpur`, `Mymensingh`, `Barishal`,
`Chittagong`).

**Standard Bangla source:** the 2,500 Standard Bangla sentences originate from the existing **Vashantor**
dataset/paper (verified via search: Vashantor's own "Bangla" split is also exactly 2,500 sentences -- Train
1,875 + Test 375 + Validation 250).

**Tiered / imbalanced parallel structure** (deliberate, not a flaw):
- **1,130 sentences** have all **7** regions filled (fully parallel core).
- An additional **370 sentences** (1,500 cumulative) additionally have **Mymensingh and Barishal** filled.
- An additional **1,000 sentences** (2,500 cumulative) have only **Pabna, Jashore, Noakhali, Rangpur** filled.
- Resulting region-wise availability: Pabna/Noakhali/Jashore/Rangpur = 2,500 sentences each; Mymensingh/Barishal
  = 1,500 each; Chittagong = 1,130.
- **Total dialect-standard sentence pairs after wide-to-long conversion: 14,130.**

**Novelty relative to prior work:** Vashantor covers Chittagong, Noakhali, Sylhet, Barishal, Mymensingh (5
regions). This project extends that coverage by adding Pabna, Jashore, Rangpur (dropping Sylhet), and also
carries Banglish/English translations (collected and validated, though not used in the final trained model --
see Part H, Limitations).

## B.2 Human Review & Validation Methodology

Three human-review guideline documents were created and followed for data quality (only the third is directly
relevant to the final delivered model, since Banglish/English were not used in training):

1. **Bangla to English review guideline** (data collected but unused in final scope) -- reviewers checked
   meaning preservation, grammar, and dialect-interpretation correctness. Status categories: Accepted / Meaning
   Change / Word Omission-Addition / Grammar Error / Unnatural Translation / Spelling Error / Dialect
   Loss-Wrong Interpretation.
2. **Banglish review guideline** (data collected but unused in final scope) -- ensures Banglish spelling
   reflects pronunciation, consistent romanization, dialect form preserved.
3. **Standard Bangla to Dialect review guideline** (this is the data actually used) -- reviewers were required
   to be native/fluent speakers of the target dialect. They ensured natural dialect usage (not respelled
   Standard Bengali), correct local grammar/pronoun/verb forms, and no unnecessary Standard-dialect mixing
   within a sentence. Status categories: Accepted / Meaning Change / Spelling Mistake / Grammar Mistake /
   Standard-Dialect Mixed.

All guidelines required keeping the original machine-assisted version and the human-corrected version as
separate files (validation evidence), with a `Review Status` column documenting corrections.

## B.3 Key EDA Findings

- Average sentence length ~6-8 words across Standard Bangla and all dialects.
- Dataset is very clean at the row level: 0 duplicate Standard Bangla sentences (at the raw-text level before
  Unicode normalization), 0 extreme-length outliers, only 1-2 rows per region flagged for stray non-Bangla
  characters out of thousands.
- **Cross-region Jaccard word-overlap similarity** (on the 1,130-sentence fully-parallel subset): **Chittagong
  is the most linguistically divergent dialect** from all others (Jaccard similarity 0.07-0.14 with every other
  region) -- consistent with linguistics literature describing Chittagonian as the most distinct Bangla dialect.
  Jashore, Mymensingh, Rangpur cluster closer together (~0.20-0.25). Pabna-Chittagong is the single most
  dissimilar pair (0.07).
- **CRITICAL finding -- "Exact-Same-as-Standard" rate per region** (fraction of a region's sentences that are
  lexically IDENTICAL to their Standard Bangla counterpart, requiring no real translation):

  | Region | Exact-Same-as-Standard % |
  |---|---|
  | Jashore | **34.84%** |
  | Rangpur | 2.24% |
  | Mymensingh | 1.07% |
  | Barishal | 1.00% |
  | Pabna | 0.92% |
  | Noakhali | 0.64% |
  | Chittagong | 0.44% |

  This is one of the most important findings in the project: **Jashore's consistently top BLEU/chrF/BERTScore
  score across every model tested is substantially explained by over a third of its "translation pairs" being
  trivial identity pairs (input already equals output)** -- not purely by Jashore being "linguistically closer"
  to Standard Bengali. Chittagong's low score, by contrast, reflects genuine translation difficulty almost
  purely (only 0.44% trivial pairs). **Always cite this alongside any Jashore-vs-Chittagong comparison.**

## B.4 Data-Quality Investigation Narrative (worth including as a rigor point in Methodology)

An automated anomaly-detection pass (comparing a trained model's per-sentence chrF against dataset targets)
initially flagged a cluster of low-scoring rows (IDs ~1041-1096, Chittagong/Noakhali) as **suspected systematic
row-misalignment** (e.g. a spreadsheet row-shift). A shift-detection script tested whether shifting the dialect
column by +/-8 rows produced a better match -- **it found no consistent single offset and no strong improvement
at any offset, ruling out systematic misalignment.** A targeted manual check (row ID 1590, Pabna) confirmed
source and target actually conveyed the same meaning; the model had simply mispredicted a hard/rare sentence.
**Lesson: a low automatic metric score does not by itself indicate a labeling error -- verify manually by
comparing source and target while deliberately ignoring the model's prediction, or risk "fixing" data that isn't
broken.** The dataset was confirmed fundamentally clean; only isolated single-row corrections (made
independently by the student, not because of this false alarm) were applied to a few Chittagong rows before
final training.

---

# PART C -- THE CRITICAL METHODOLOGICAL FIX: Train-Test Leakage

**This is the single most important technical/methodological narrative in the whole project -- always describe
it as a strength (rigor demonstrated), never hide or minimize it.**

## C.1 What Went Wrong (First Attempt)

The dataset was reshaped from wide format (one row per Standard Bangla sentence, columns per dialect) into a
long format (one row per dialect-standard pair) for sequence-to-sequence training, with region-tagged source
text: `"translate {region} to Bangla: {dialect sentence}"` -> target: the Standard Bangla sentence.

The **first** train/validation/test split was done **at the row level**, stratified by region (80/10/10,
seed=42). This was flawed: because the **same Standard Bangla sentence is the target for up to 7 different
rows** (one per region that has it), a row-level split could place different regional variants of the *same*
underlying sentence into different subsets -- e.g. the Chittagong version of sentence #482 in training, the
Pabna version of the *same* sentence #482 in test. Since the **target text is identical** in both, the model
could memorize the answer from training and reproduce it at test time without genuinely translating the *new*
input it saw at test time.

**Discovery:** comparing unique target sentences in test vs. train showed nearly 100% overlap. Manual inspection
found individual test predictions that were **exact character-for-character matches** to the target -- consistent
with memorization, not translation. This coincided with a suspiciously inflated evaluation score (~82.85 BLEU on
one early run) that prompted the investigation.

## C.2 The Fix (Two-Stage, Final Version)

**Stage 1 -- ID-grouped split:** switched from row-level splitting to grouping by the original sentence `ID`.
All regional variants that share the same `ID` are now assigned to the **same** subset (train, val, or test) as
a group. Implementation: get the list of unique `ID`s, split *that list* 80/10/10 with `train_test_split`
(seed=42), then filter the long-format pairs table by ID membership into train/val/test.

**Stage 2 -- Normalized-target dedup linking (a further refinement found later):** even after ID-grouping, a
second, subtler leakage vector was found: **two *different* IDs can, by coincidence, have the exact same
Standard Bangla sentence text** (confirmed: of 2,500 unique IDs, only **2,499 unique normalized target
sentences** -- exactly one pair of IDs shares an identical target). The final pipeline links such ID-pairs into
the same split group too, so no target sentence text can appear in more than one split regardless of which
ID(s) produced it.

**Post-split verification (must always be run and printed before training):**
- ID overlap: train-val = 0, train-test = 0, val-test = 0 (PASS)
- Target-text overlap: train-val = 0, train-test = 0, val-test = 0 (PASS)

**Final split sizes (unique IDs / pairs):** Unique-ID split: 2,000 / 250 / 250 (train/val/test). Pair split:
**11,316 train / 1,395 validation / 1,419 test.**

## C.3 Why This Matters / How to Describe It

> "An independent re-execution of the entire pipeline (data preparation, ID-grouped split, balancing, training,
> and evaluation) with the same random seed reproduced results identical to four decimal places, confirming the
> determinism of the training procedure and the validity of the reported evaluation methodology."

Frame this in the report as evidence of rigor: the project diagnosed a non-obvious data-leakage risk specific to
this dataset's structure (one target shared across many source rows) and corrected the experimental design
*before* finalizing results, rather than accepting an inflated number.

---

# PART D -- FULL, FINAL, LOCKED RESULTS

## D.1 Preprocessing Pipeline (in exact order -- reproduce in this order)

1. **Text cleaning** on every text column: Unicode **NFC normalization** (Bengali glyphs can have more than one
   valid byte-level encoding for the same visual character -- this affected a large fraction of rows: e.g.
   Standard Bangla had 993 rows with NFC changes, 1,086 rows changed by cleaning overall; Pabna had 1,375 NFC
   changes affecting 1,533 rows -- this was a real, non-trivial issue, not just theoretical caution), removal of
   zero-width/invisible Unicode characters, and whitespace collapsing/trimming.
2. **Wide-to-long conversion** with the region-tagged task prefix (see C.1).
3. **ID-grouped 80/10/10 split + normalized-target dedup linking** (see Part C) + leakage audit (must show all
   0/0/0 overlaps before proceeding).
4. **Train-only regional balancing:** every region's *training* subset is resampled to a common target of
   **2,000 pairs** -- regions with fewer than 2,000 (Mymensingh 1,204->2,000; Barishal 1,204->2,000; Chittagong
   908->2,000) are resampled **with replacement**; regions already at/above 2,000 (Pabna, Noakhali, Jashore,
   Rangpur -- all exactly 2,000) are left as-is. **Validation and test sets are never touched by balancing.**
   Note for Discussion: Chittagong's balanced 2,000 training examples still contain only 908 *unique* underlying
   pairs -- oversampling increases training exposure but cannot manufacture new linguistic information.
   **Final balanced training set size: 14,000 pairs** (11,316 -> 14,000).
5. **Token-length selection:** computed from the actual data distribution -- source mean 19.15 tokens, target
   mean 8.10 tokens; 99.5th-percentile source length 34, target 17; maximum observed source 48, target 23.
   **Selected: `MAX_SOURCE_LEN = 40`, `MAX_TARGET_LEN = 32`** (source truncation rate at this length: 0.09%;
   target truncation: 0.00%).

## D.2 Model & Training Configuration (exact, reproducible)

- **Base model:** `csebuetnlp/banglat5` (also separately: `google/mt5-base`, `google/mt5-small` for comparison
  runs, same recipe).
- **Framework:** Hugging Face `transformers` (a very recent v5.x release was in use in the Colab environment --
  note two breaking API changes vs older tutorials: `Seq2SeqTrainer(tokenizer=...)` is now
  `processing_class=...`, and `Seq2SeqTrainingArguments(warmup_ratio=...)` is now `warmup_steps=...` accepting a
  float <1 as a ratio).
- **Known bug avoided:** `fp16=True` causes training loss to collapse to exactly 0 and validation loss to become
  `NaN` for T5-family models (a documented numeric-overflow issue). **Always use `fp16=False`.**
- **Training arguments (the confirmed final recipe):**
  - `num_train_epochs = 12` (hard cap; early stopping typically triggers around epoch 8-11 in practice)
  - `label_smoothing_factor = 0.1`
  - `lr_scheduler_type = "cosine"`, `warmup_steps = 0.1` (ratio), `learning_rate = 1e-4`
  - `max_grad_norm = 1.0` (explicit gradient clipping)
  - `weight_decay = 0.01`
  - `per_device_train_batch_size = 16`, `per_device_eval_batch_size = 16`
  - `eval_strategy = "epoch"`, `save_strategy = "epoch"`, `save_total_limit = 2`
  - `load_best_model_at_end = True`, `metric_for_best_model = "eval_loss"` (never select by test BLEU)
  - `EarlyStoppingCallback(early_stopping_patience = 3)`
  - `seed = 42`, `data_seed = 42` (plus `transformers.set_seed(42)` called globally before training)
  - For BanglaT5 specifically: training converged with best validation loss **2.3942** at **epoch 8**
    (`checkpoint-7000`); early stopping ended training around epoch 11; actual wall-clock training time varied
    73-87 minutes across repeated runs on Colab (GPU-allocation variance, not a methodology difference --
    results were numerically identical to 4 decimal places across reruns).
- **Decoding (selected via a grid search on the *validation* set only, never on test):** tested beam widths 1,
  4, 6 on validation; **beam = 4** selected (validation BLEU 50.86 / chrF 75.42 vs. beam 6's near-identical
  50.83 / 75.38 -- beam 4 chosen as the simpler, equally-good option). Final generation settings:
  `num_beams=4, max_new_tokens=32, length_penalty=1.0, early_stopping=True`.

## D.3 Evaluation Methodology

**Four metrics used together, deliberately spanning two lexical and two semantic measures:**
1. **BLEU** (`sacrebleu`) -- lexical, n-gram precision.
2. **chrF** (`sacrebleu`) -- lexical, character-level F-score (more forgiving of Bengali morphology than
   word-level BLEU).
3. **BERTScore** (`bert-base-multilingual-cased`, `lang="bn"`) -- semantic, token-level embedding alignment.
4. **STS Cosine Similarity** -- semantic, **sentence-level** embedding similarity using
   `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (whole-sentence embedding, cosine similarity
   between prediction and reference). **COMET was considered and deliberately rejected** as the 4th metric
   because the `unbabel-comet` library has known dependency conflicts with very recent `transformers` releases
   (a real risk given the environment's transformers v5) -- sentence-embedding cosine similarity was chosen as a
   stable, low-risk alternative that is still methodologically distinct from BERTScore (whole-sentence vs.
   token-level comparison).

**Critical evaluation-correctness rule:** predictions AND references must be passed through the **same**
normalization function (Unicode NFC + zero-width removal + whitespace cleanup) **before any metric is
computed** -- applied immediately after generating predictions, before BLEU/chrF/BERTScore/STS/exact-match are
calculated. (This was itself a bug found and fixed during development: an earlier version normalized too late,
after some metrics had already been computed on raw text, causing two evaluation runs of the same model to
disagree by ~0.1-0.15 BLEU points until this was corrected.)

**Confidence intervals:** bootstrap resampling (300 iterations) must resample **unique sentence IDs**, not
individual row indices -- because multiple regional rows sharing the same ID are not independent observations,
row-level bootstrap would produce artificially narrow confidence intervals.

**A firm rule followed throughout:** dataset target sentences must never be edited to match a model's
prediction, even if the prediction looks equally or more natural -- that would be circular validation. The only
legitimate reason to edit a target is an independent check (comparing source and target directly, blind to any
model's prediction) confirming a genuine original annotation error.

## D.4 FINAL RESULTS TABLE -- Three Models, Four Metrics, Same Pipeline

**Overall (test set, 1,419 pairs):**

| Model | BLEU | chrF | BERTScore F1 | STS Cosine Sim. |
|---|---|---|---|---|
| **BanglaT5** | **50.87** | **75.34** | **0.9392** | **0.9195** |
| mT5-base | 47.60 | 72.75 | 0.9324 | ~0.910 |
| mT5-small | 43.58 | 70.06 | 0.9241 | 0.8884 |

(BanglaT5's BLEU 95% CI: [47.57, 53.94]; chrF 95% CI: [73.29, 77.21]; exact-match rate 24.81%; Best_Checkpoint =
`checkpoint-7000`; Best_Validation_Loss = 2.3942.)

**Per-region, BanglaT5 (the final selected model):**

| Region | Test N | BLEU | chrF | BERTScore F1 | STS Cosine Sim. | Exact-Match % |
|---|---|---|---|---|---|---|
| Jashore | 250 | 69.31 | 86.98 | 0.9696 | 0.9627 | 41.20 |
| Rangpur | 250 | 54.14 | 79.40 | 0.9475 | 0.9326 | 26.40 |
| Pabna | 250 | 50.63 | 74.52 | 0.9349 | 0.9076 | 24.40 |
| Noakhali | 250 | 47.49 | 73.60 | 0.9357 | 0.9260 | 20.80 |
| Barishal | 153 | 44.17 | 71.36 | 0.9314 | 0.9246 | 17.65 |
| Mymensingh | 153 | 41.73 | 69.15 | 0.9273 | 0.9146 | 18.30 |
| Chittagong | 113 | 31.63 | 60.65 | 0.8976 | 0.8685 | 13.27 |

**Per-region, mT5-base:** Jashore 72.37/87.44/0.9684/0.9549; Rangpur 49.34/76.14/0.9403/0.9192; Pabna
47.72/72.43/0.9284/0.8886; Noakhali 42.93/71.07/0.9322/0.9181; Barishal 38.58/67.76/0.9221/0.9001; Mymensingh
35.28/64.92/0.9149/0.8989; Chittagong 25.25/55.27/0.8828/0.8453 (format: BLEU/chrF/BERTScore/STS).

**Per-region, mT5-small:** Jashore 73.99/88.10/0.9693/0.9579; Rangpur 43.90/73.07/0.9295/0.8965; Pabna
39.34/67.68/0.9147/0.8605; Noakhali 38.39/68.74/0.9249/0.8997; Barishal 34.42/64.07/0.9122/0.8727; Mymensingh
31.48/62.07/0.9043/0.8667; Chittagong 20.54/51.42/0.8739/0.8037.

## D.5 Key Findings for Discussion/Conclusion Chapter (all confirmed, ready to write)

1. **Dialect linguistic distance correlates with translation difficulty.** Chittagong is both the most lexically
   distant dialect (Jaccard similarity 0.07-0.14, Part B.3) and consistently the hardest for every model on every
   metric.
2. **Jashore's top score is substantially a dataset artifact, not pure linguistic proximity.** 34.84% of
   Jashore's sentences are lexically identical to Standard Bengali (Part B.3) -- always cite this alongside any
   Jashore result.
3. **Language-specific pretraining beats generic multilingual pretraining.** BanglaT5 outperformed mT5-base on
   every single region across all four metrics -- consistent with the same pattern reported in the Vashantor
   paper for their "DialectBanglaT5" fine-tune.
4. **Model capacity has a non-monotonic, task-dependent effect (a novel, publication-worthy finding).** Within
   the mT5 family, the *smaller* mT5-small scored *higher* than mT5-base specifically on Jashore (73.99 vs.
   72.37 BLEU) -- the near-identical-copy nature of many Jashore pairs rewards a smaller, less "creative" model
   that reproduces input more literally. On genuinely hard dialects (Chittagong), the pattern reverses as
   expected: mT5-base (25.25) beats mT5-small (20.54). **Averaging performance across regions can hide this
   architecturally meaningful, region-specific behavior.**
5. **Metrics can disagree, validating the multi-metric approach.** On mT5-base, lexical metrics (BLEU, chrF,
   BERTScore) all rank Pabna above Noakhali, but STS cosine similarity ranks Noakhali above Pabna (0.9181 vs.
   0.8886) -- a concrete example of surface-level vs. embedding-level evaluation diverging.
6. **Full pipeline reproducibility confirmed:** independent re-runs with the same seed produced BanglaT5 results
   identical to 4 decimal places.
7. **Literature validates several design choices:** Chittagong's difficulty is corroborated across multiple
   independently reviewed papers (WER 76% even with retrieval-augmentation in one; lowest human-rated fluency in
   another; described as a "semi-language" in a linguistics source) -- cite these to contextualize the model's
   Chittagong performance as an expected, documented challenge rather than a flaw. Separately, a
   Lebanese-dialect paper's finding that authentic, native-validated small datasets outperform larger synthetic
   ones directly supports this project's native-speaker-validated data-collection approach (as opposed to other
   reviewed papers that used LLM-generated synthetic Banglish/dialect data).

---

# PART E -- MODELS ATTEMPTED BUT NOT IN THE FINAL COMPARISON

- **IndicBARTSS** (`ai4bharat/IndicBARTSS`) -- a dedicated Indic-language mBART-style model, attempted as a
  potential 3rd/4th comparison model. **Excluded from the final comparison** due to an unresolved
  tokenizer/generation-configuration bug: this architecture requires special language-tag tokens (`<2bn>`)
  rather than a plain text prefix, and two distinct issues occurred -- (a) a `decoder_start_token_id` mismatch
  between training and generation configs caused fluent but semantically wrong output despite a healthy,
  converging training loss (a useful lesson: a good loss curve does not guarantee correct generation config),
  and (b) after a partial fix, `skip_special_tokens=True` did not fully strip this tokenizer's added
  language-tag tokens from decoded output, artificially deflating BLEU/chrF further. Given the project deadline,
  this was disclosed as a limitation rather than risking an unreliable reported number.
- A **two-stage framework** (a separate dialect-identification classifier feeding into the translation model)
  was suggested by outside research advice and is a legitimate idea, but was **not implemented** -- the current
  model requires the user/caller to specify the region manually (see Part G, web interface spec). This is a
  disclosed limitation / future-work item, not part of the delivered system.
- **RAG-based translation**, **COMET evaluation**, **multi-reference evaluation**, and **synonym-based data
  augmentation** were all considered (based on external research-methodology advice and literature review) and
  explicitly **not attempted** due to time constraints and/or dependency-risk -- each is noted as future work.
- A **multi-task ablation** (adding Banglish/English as auxiliary training tasks alongside dialect->standard)
  was discussed as a way to use the unused Banglish/English data, but the student explicitly chose **not** to
  attempt it -- Banglish/English remain collected-and-validated-but-unused data, to be mentioned as dataset
  richness / future work in the report (see Part F).

---

# PART F -- REPORT-WRITING STATUS & GUIDANCE

## F.1 What Exists So Far

- Chapters 1, 2, 3 (partially), and 5 have been drafted by the student in a file called
  `Before_formating_report.docx`. **This has not yet been reviewed for consistency with the actual work
  described in this document** -- before editing it, read it and cross-check every claim against Parts A-E
  above, flagging any mismatch (e.g., if it describes a bidirectional system, that must be corrected to match
  the final single-direction scope).
- Chapter 3 (Methodology) template required by the department:
  ```
  3.1 Methodology (research framing -- NOT "Requirement Analysis & Design Specification," which is for
      software/project-type theses)
    3.1.1 Overview
    3.1.2 Proposed Methodology (research framing -- NOT "System Design")
    3.1.3 Functional and Nonfunctional Requirements
    3.1.4 Data Flow Diagram
    3.1.5 UI Design
  3.2 Detailed Methodology and Design (must discuss alternate solutions considered and why the final one was
      chosen -- use Part E above for this)
  3.3 Project Plan
  3.4 Task Allocation (a week-12-to-week-48 timeline table)
  3.5 Summary
  ```
- Chapter 3, Sections 3.1-3.1.2 (Overview + Proposed Methodology, Steps 1-6) have already been drafted in formal
  academic English, describing: data collection -> human review -> preprocessing/cleaning -> ID-grouped
  leakage-safe splitting -> balancing -> model fine-tuning -> evaluation. Continue from there in the same tone/
  register for 3.1.3 onward, using Parts B-D above as the factual source.
- A methodology pipeline diagram (4-phase flowchart: Data Collection & Human Validation -> Preprocessing &
  Leakage-Safe Splitting -> Model Fine-Tuning -> Evaluation) has already been created as an image
  (`Methodology_Diagram.png`) for use as Figure 3.1.
- Chapter 3 should **not** contain specific result numbers -- those belong in the Results chapter (Chapter 4),
  using the tables in Part D.4 above directly.

## F.2 Ground Rules for Any AI Continuing This Report

1. Do not invent facts/numbers not present in this document -- ask the student rather than guessing.
2. Do not describe the system as bidirectional or mention a "hybrid model" as delivered -- only as considered-
   and-descoped alternatives (Part A.1, Part E).
3. Treat the train-test leakage discovery/fix (Part C) as a demonstrated strength, not a weakness.
4. Disclose IndicBARTSS's exclusion honestly (Part E) rather than omitting it.
5. Use formal, impersonal academic register ("the dataset was collected..." not "I collected...").
6. For Section 3.1.5 (UI Design): this is a research project delivering a trained model, not originally an
   end-user application -- either state plainly that no interface was part of the core research deliverable
   (the web interface, if finished by the time of writing, is a separate/supplementary artifact -- see Part G),
   or ask the student directly what to say here, rather than assuming.
7. For Section 3.3/3.4 (Project Plan/Task Allocation table): ask the student for actual week numbers/phase
   proportions rather than inventing a plausible-looking schedule.
8. Write in parts, pausing after each subsection for the student's review, rather than generating the whole
   remaining report in one pass.

---

# PART G -- WEB INTERFACE SPECIFICATION

## G.1 What to Build

A simple web page: user selects a **region** (dropdown, single-select, exactly these 7 values:
`Pabna, Noakhali, Jashore, Rangpur, Mymensingh, Barishal, Chittagong`), types a **dialect sentence** into a text
box, clicks **Translate**, and sees the **Standard Bengali translation** appear as output. No login, no
database, no multi-page navigation needed. No support for the reverse direction, and no Banglish/English input
support (untrained/untested for those).

## G.2 CRITICAL: Exact Input Format Required

```
translate {region} to Bangla: {dialect_sentence}
```
`{region}` must be exactly one of the 7 strings above (exact spelling/capitalization). Example: selecting
"Chittagong" and typing "kemon acho" style text must send the model the literal string
`"translate Chittagong to Bangla: <the Bengali-script dialect sentence>"`. Do not translate or alter the English
words "translate"/"to"/"Bangla" in this prefix -- the model was trained on this literal template.

## G.3 Exact Inference Settings (must match evaluation to get reported-quality output)

```python
inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=40)
output_ids = model.generate(
    **inputs,
    max_new_tokens=32,
    num_beams=4,
    length_penalty=1.0,
    early_stopping=True,
)
translated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
```

## G.4 Model Location -- Must Be Moved Out of Colab First

The trained model currently exists only inside the Colab session that trained it (path like
`banglat5_final_outputs/banglat5_model` or a `checkpoint-7000` folder), which is **ephemeral**. Before building
the web app, push it to the Hugging Face Hub (run once, in that Colab session):

```python
from huggingface_hub import login
login()  # paste a free Hugging Face access token
model.push_to_hub("your-username/banglat5-dialect-to-standard")
tokenizer.push_to_hub("your-username/banglat5-dialect-to-standard")
```

Then any web app can load it from anywhere with:
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = AutoTokenizer.from_pretrained("your-username/banglat5-dialect-to-standard")
model = AutoModelForSeq2SeqLM.from_pretrained("your-username/banglat5-dialect-to-standard")
```

## G.5 Recommended Tech Stack: Gradio

For a text-in/text-out ML demo like this, **Gradio** (a Python-only library) is recommended over building a
separate frontend+backend -- one Python file, no HTML/CSS/JS needed, free deployment via Hugging Face Spaces. A
working starter `app.py` has already been created (see G.6) with: a region dropdown, a multi-line input
textbox, a Translate button, an output textbox, a few example sentences, and basic empty-input error handling.
(Alternative: Streamlit, similar simplicity with more layout control. A custom Flask/HTML build is possible but
unnecessary extra work for this use case.)

## G.6 Starter Code Already Written

A complete, working Gradio app (`app.py`) and a full requirements document
(`Web_Interface_Requirements.md`) covering all of the above in more detail (including a functional/non-functional
requirements checklist) have already been created. If not available in a new session, recreate `app.py` using
the exact input format (G.2), inference settings (G.3), and model path (G.4) above -- the structure is: load
model once at startup, define a `translate(region, sentence)` function implementing G.2-G.3, wire it to a
`gr.Dropdown` + `gr.Textbox` + `gr.Button` + output `gr.Textbox` via Gradio Blocks, call `demo.launch()`.

---

# PART H -- LIMITATIONS (for the thesis Limitations section)

- IndicBARTSS excluded from the final comparison due to an unresolved tokenizer/generation-config bug (Part E)
  -- a disclosed tooling limitation, not a reflection of the architecture's true capability.
- The system requires the caller to specify the input's region manually; no automatic dialect-identification
  stage was implemented (considered, not built -- Part E).
- Banglish and English translations were collected and human-validated alongside the dialect data but were not
  incorporated into model training; a multi-task ablation using them was considered but not attempted, and is
  left as future work.
- Multi-reference evaluation, COMET, RAG-based translation, and synonym-based data augmentation were all
  considered (via literature review and external methodology research) but not attempted, due to time
  constraints and/or dependency-conflict risk (COMET specifically).
- Statistical significance testing (e.g., paired bootstrap comparing BanglaT5 vs. mT5-base directly) was
  identified as a possible further step but was not performed -- a natural next step if time allows.
- A bidirectional system and a region-routing "hybrid" ensemble were explored as ideas but descoped from the
  final delivered system due to the project timeline.

---

*End of master document. This file is intended to be sufficient on its own; if any supplementary file mentioned
above (dataset spreadsheet, literature review sheet, guideline PDFs, notebooks, `Before_formating_report.docx`,
`Methodology_Diagram.png`, `Web_Interface_Requirements.md`, `app.py`) is available, providing it alongside this
document will help but should not be strictly necessary to continue the work.*
