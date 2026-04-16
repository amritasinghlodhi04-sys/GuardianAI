# GuardianAI Current MVP Status

## Purpose of this document
This document compares the current implementation with the expected MVP described in `HOW-TO-USE.md` and `MY-ROLE.md`.

---

## 1) What happens when you run this command

Command:

`python -m guardianai -i demo_assets/official.jpg --offline-images demo_assets/candidates --threshold 0.9`

Step-by-step runtime flow:

1. Python starts module entrypoint `guardianai.__main__`, which calls CLI `main()`.
2. `.env` is loaded (if present) so optional settings like `GEMINI_API_KEY` are available.
3. CLI arguments are parsed:
   - input file: `demo_assets/official.jpg`
   - candidate source: `demo_assets/candidates`
   - threshold: `0.9`
4. Validation checks source mode:
   - Since `--offline-images` is provided, Instagram fetching is skipped.
5. CLIP model is loaded (`ViT-B/32`) through `ClipEmbedder.create()`:
   - selects device (`cuda`, `mps`, else `cpu`)
   - first run may download model weights
6. Query embedding is created:
   - input is an image, so one embedding vector is generated for `official.jpg`
   - vectors are L2 normalized
7. Candidate image collection:
   - recursively scans `demo_assets/candidates`
   - keeps files with supported image suffixes (`.jpg`, `.jpeg`, `.png`, `.webp`)
8. Candidate embeddings are generated in batches using the same CLIP preprocess/model.
9. Similarity scoring:
   - cosine similarities are computed between query embeddings and candidate embeddings
   - best score and best matching candidate path are selected
10. Decision:
    - if `best_score >= 0.9`, output `Flag as potential misuse (prototype): YES`
    - else output `NO`
11. Console output prints:
    - media path, mode, candidate count, best cosine score, closest candidate file, final flag
12. Since `--report` is not passed in your command, Gemini reporting is not executed.

---

## 2) Is `gemini_report` providing report?

Short answer: **Yes, but only when enabled and configured.**

Conditions required:

1. You pass `--report` in command.
2. `GEMINI_API_KEY` exists in environment or `.env`.
3. `google-generativeai` package is installed.
4. Gemini API call succeeds.

Behavior:

- If all conditions pass, `try_generate_report()` returns a short bullet summary.
- If key is missing or API call fails, output falls back to:
  - `(Gemini skipped: set GEMINI_API_KEY in environment or .env)`
- If you do not pass `--report`, Gemini is not called.

---

## 3) MVP comparison against `HOW-TO-USE.md`

| Requirement from HOW-TO-USE | Status | Current implementation |
|---|---|---|
| CLI entrypoint via `python -m guardianai` | Covered | Implemented and working |
| Compare official image vs folder (`--offline-images`) | Covered | Implemented in pipeline |
| Compare official video vs folder (`--max-frames`) | Covered | Frame extraction + embedding implemented |
| Compare against public Instagram user (`--ig-user`) | Covered | Implemented using Instaloader |
| Threshold-based flagging (`--threshold`) | Covered | Uses cosine best-score decision |
| Optional Gemini narrative (`--report`) | Covered | Implemented with graceful fallback |
| Print clear demo output summary | Covered | Implemented in `format_result_lines()` |
| Setup docs for Windows/macOS/Linux | Covered | Present in `HOW-TO-USE.md` |
| Reliability fallback if Instagram fails | Covered | Error messaging recommends offline mode |
| Whole-internet scanning | Not in scope by design | Explicitly not part of prototype |

MVP conclusion for HOW-TO-USE:

**Current code satisfies the documented prototype MVP.**

---

## 4) Comparison against `MY-ROLE.md`

`MY-ROLE.md` describes a broader production-style pipeline. Current implementation is a focused prototype subset.

| MY-ROLE expectation | Status | Notes |
|---|---|---|
| CLIP embedding generation | Covered | Implemented (`ClipEmbedder`) |
| Vector DB storage (Pinecone) | Not covered | No Pinecone integration in current code |
| Broad web crawler (Twitter/Reddit/news) | Not covered | Current sources are IG public profile or local folder |
| Similarity search against persistent vector store | Partial | Similarity exists, but in-memory per-run; no persistent vector DB |
| Gemini report generation | Covered (optional) | Implemented when `--report` + API key |
| Send alert to backend API | Not covered | No outbound webhook/API call currently |
| Real-time continuous scanning | Not covered | Current CLI is one-shot execution |
| Presenter-ready flow for judges | Covered for prototype | Offline demo mode is reliable for presentation |
| Google Vision / Google Cloud integration | Not covered | Not used in current implementation |

Conclusion vs MY-ROLE:

- **Core AI matching + optional Gemini summary are implemented.**
- **Platform-style components (Pinecone, broad scraping, backend alerting, cloud ops) are next-phase work.**

---

## 5) Google technologies currently used

Currently used:

1. **Google AI Studio API key** workflow (`GEMINI_API_KEY`).
2. **Gemini model via `google-generativeai`** package.
3. Default model id: `gemini-1.5-flash` (override with `GEMINI_MODEL`).

Not currently used (mentioned in broader role vision, but absent in code):

- Google Vision API
- Google Cloud Storage
- Google Cloud Run / Functions
- BigQuery / PubSub / Vertex AI services

---

## 6) Feature list of current work

Implemented features:

1. CLI-based prototype workflow.
2. Image input and video input support.
3. Video frame sampling and embedding.
4. Local folder candidate matching (stable demo path).
5. Public Instagram profile image download + matching.
6. CLIP-based cosine similarity scoring and threshold decision.
7. Best-match file path reporting.
8. Optional Gemini-generated narrative summary.
9. `.env` support for secrets/config.
10. Temporary Instagram download cleanup.

Known prototype constraints:

1. Single run / no scheduler.
2. No persistent index/vector DB.
3. No automated legal workflow / no takedown integration.
4. No backend dashboard or API integration.
5. No web-scale source coverage.

---

## 7) Recommended next steps (priority order)

### High priority (to align with MY-ROLE)
1. Add persistent vector storage (Pinecone) for official media.
2. Add ingestion command for official assets (`guardianai ingest ...`).
3. Add scanner command to compare discovered assets against stored vectors.
4. Add backend alert POST integration for detected violations.

### Medium priority
5. Add structured result output (`json`) for dashboard/API consumption.
6. Add richer evidence bundle (top-k matches, timestamps, thumbnails).
7. Add retry/backoff + better diagnostics for Instagram/network failures.

### Demo/presentation upgrades
8. Add a single "judge demo" script that runs deterministic offline scenario.
9. Add precision/recall validation set and threshold tuning report.
10. Add one-slide architecture diagram generated from current code path.

---

## 8) Current MVP verdict

For the MVP defined in `HOW-TO-USE.md`:

- **Status: Achieved**

For the larger product vision in `MY-ROLE.md`:

- **Status: Partially achieved (prototype core complete, platform components pending)**

