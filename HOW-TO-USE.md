# GuardianAI — How to use (setup, demo, new machine)

This prototype answers: **“Does my image or video look like anything on a single public Instagram profile (or a local folder of images)?”**  
It uses **CLIP** (runs locally, free) and optional **Gemini** (free API key from Google AI Studio). **No paid services are required** for the core demo.

---

## What this prototype does (and does not do)

- **Does:** Embeds your official image (or sampled video frames) and compares them to images from:
  - a **public** Instagram username’s **most recent N posts** (via [Instaloader](https://github.com/instaloader/instaloader), free), or  
  - a **folder of images** you provide (best for a reliable hackathon demo).
- **Does not:** Search the whole internet or all platforms. That would need scale, APIs, and compliance work beyond a prototype.
- **Instagram:** Only **public** profiles; Instagram may rate-limit or block automated access. If that happens, use **`--offline-images`** for your presentation.

---

## Prerequisites

- **Python 3.10+** ([python.org](https://www.python.org/downloads/) or your OS package manager).
- **Internet** on first run (downloads CLIP weights; Instagram path needs network).
- **Disk:** a few GB for PyTorch + CLIP + dependencies.

---

## One-time setup (this machine or any other: Windows, macOS, Linux)

Open a terminal **in the `GuardianAI` folder** (the one that contains `requirements.txt`).
(install python if not already: winget install -e --id Python.Python.3.11)
### 1) Create and activate a virtual environment

**Windows (PowerShell or Command Prompt):**

```text
python -m venv .venv (or py -m venv .venv)
.\.venv\Scripts\activate
```

**macOS / Linux:**

```text
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in the prompt.

### 2) Upgrade pip and install dependencies

```text
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The first run of the tool will download **CLIP ViT-B/32** weights (may take a few minutes).

### 3) Optional — Gemini report (`--report`)

1. Open [Google AI Studio](https://aistudio.google.com/) and create a **free API key**.
2. Copy `.env.example` to `.env` in the same `GuardianAI` folder. (use command: Copy-Item .env.example .env)
3. Set `GEMINI_API_KEY=your_key_here` inside `.env`.

If you skip this, the tool still runs; only the optional narrative report is omitted.

---

## Commands to run a demo

Always activate the venv first (see above). Run commands from the **`GuardianAI`** directory.

### CLI help

```text
python -m guardianai --help
```

---

### Demo A — Reliable: compare against a **folder of images** (recommended for judges)

1. Put your **official** file in `demo_assets`, e.g. `demo_assets/official.jpg`.
2. Create a folder of **candidate** images, e.g. `demo_assets/candidates/`, and include:
   - a **copy** of the same image (renamed), or  
   - screenshots / crops that should look similar.

3. Run:

```text
python -m guardianai -i demo_assets/official.jpg --offline-images demo_assets/candidates --threshold 0.88 --report
```

- If the best cosine similarity is **above** `--threshold`, the prototype prints **potential misuse: YES** (this is a similarity heuristic, not legal proof).

**Video:**

```text
python -m guardianai -i demo_assets/clip.mp4 --offline-images demo_assets/candidates --max-frames 8
```

---

### Demo B — Instagram: one **public** username (recent posts only)

Pick a **public** account that posts photos (not only Reels-only, if possible, so there are images to compare).

```text
python -m guardianai -i demo_assets/official.jpg --ig-user SOME_PUBLIC_USERNAME --max-posts 8
```

- Lower `--max-posts` for faster runs.
- If Instagram blocks or returns no images, use **Demo A** instead.

---

### Demo C — Optional Gemini narrative

With `.env` containing `GEMINI_API_KEY`:

```text
python -m guardianai -i demo_assets/official.jpg --offline-images demo_assets/candidates --report
```

---

## Setting up on another computer (e.g. iMac after Windows)

1. Copy the whole **`GuardianAI`** project folder (or clone from git).
2. On the new machine, repeat **One-time setup**: create venv, `pip install -r requirements.txt`.
3. Copy your **`.env`** if you use Gemini (do not commit `.env`).
4. Run the same **Commands to run a demo** as above.

PyTorch will install the correct wheel for that OS (including Apple Silicon).

---

## Optional: Docker (Linux image)

Only if you need a Linux environment; ML on Mac inside Docker is often CPU-only. From `GuardianAI`:

```text
docker build -t guardian-ai .
docker run --rm -it -v "%cd%":/app -w /app guardian-ai python -m guardianai --help
```

(On PowerShell, use `${PWD}` or the full path instead of `%cd%` if needed.)

---

## Troubleshooting

| Issue | What to try |
|--------|-------------|
| `No module named 'guardianai'` | Run from the `GuardianAI` folder; use `python -m guardianai`. |
| Instagram: no images / login / rate limit | Use `--offline-images` for the demo. |
| CLIP download slow | First run only; keep the venv on disk. |
| Gemini errors | Check `GEMINI_API_KEY`; try `GEMINI_MODEL=gemini-1.5-flash` in `.env`. |

---

## Legal / ethics (prototype)

Respect Instagram’s terms, copyright, and privacy. Use **public** data only for a competition demo; real enforcement needs proper process and legal review. Similarity scores can produce **false positives**; human review is required.
