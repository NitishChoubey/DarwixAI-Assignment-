# DarwixAI AI Engineer assessment

Working prototypes for all four questions in **one repository**. Evaluation is about grounded answers, measurable results, and failure handling — not a pretty shell.

| Question | What to open | Evidence |
|---|---|---|
| 1 Voice agent | `/agent` | `docs/q1_test_calls.md` |
| 2 Knowledge base | `/kb` | `docs/q2_knowledge_base.md`, `docs/q2_retrieval_tests.md`, `data/kb/build_report.md` |
| 3 Native bots | `/native` | `docs/q3_localization.md`, `docs/q3_test_calls.md` |
| 4 Live nudges | `/live` | `docs/q4_latency.md` |

Architecture, limitations, video script: `docs/`.

## What “Sentinel Health” is

The PDF asks you to pick **one** Q1 use case. This submission uses **health-insurance lead qualification**.

**Sentinel Health Insurance** is a *fictional* insurer created so Question 2 can ingest messy business content (website + PDF + tables + outdated brochure + PII + a corrupted scan) without copying a real company’s documents. The Q1 bot qualifies Sentinel leads by **retrieving** that knowledge base. FAQs, objections and waiting periods are not hardcoded in the prompt.

Question 3 is **not** Sentinel Health in Filipino. Philippines = ShieldLife × Banco Isla bancassurance. Indonesia = MitraDana multifinance. Same engine, different KB slice and locale pack.

## Setup (Windows / PowerShell)

```powershell
cd "d:\DarwixAI Assignment"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# put OPENAI_API_KEY in .env if you have one (LLM, Whisper, embeddings).
# Without a key the KB (BM25), template agent, Edge TTS, and Q4 rules still run.
```

Rebuild the knowledge base (India + PH + ID sources):

```powershell
python -m q2_knowledge_base.pipeline --no-embed
python -m q2_knowledge_base.retrieval_tests
python -m q1_voice_agent.test_calls
python -m q3_native_bots.test_calls
python -m q4_live_nudges.simulate --fast
python -m app
```

Then open http://127.0.0.1:8000

With an API key, drop `--no-embed` so retrieval becomes hybrid BM25 + `text-embedding-3-small`. Web calling uses Whisper on `/agent` and `/native`; Edge TTS supplies native `fil-PH` and `id-ID` voices.

## Design choices (short)

- **Web calling UI** rather than a PSTN number — the PDF allows either; this is fully demoable without buying a DID.
- **Grounding confidence is absolute.** Out-of-scope questions must come back “I don’t have that information”, not a best-effort hallucination.
- **Qualification is a Python engine** copied from the underwriting grid. The model is not allowed to say “approved”.
- **Q4 is chunked real-time replay** (`time.sleep` per turn/chunk). Analysing a finished file after upload is a rejection condition.
- **Nudge spam is controlled:** confidence threshold, cooldown, duplicate evidence, TTL, priority.

Do not commit `.env`, keys, or real customer data.

## Remaining git commits (you already pushed 1–6)

You are on `994d9b1` (Q1 agent core). Commit the rest yourself in this order:

**7 — Q1 web calling + tests**
```powershell
git add q1_voice_agent/agent.py q1_voice_agent/api.py q1_voice_agent/static/ q1_voice_agent/test_calls.py docs/q1_test_calls.md data/crm/ data/transcripts/q1_*.json
git commit -m "Add web calling UI, CRM leads and Q1 test-call transcripts"
```

**8 — Q3 localized KB (not a translation of Sentinel)**
```powershell
git add q3_native_bots/philippines/ q3_native_bots/indonesia/
git commit -m "Add Philippines bancassurance and Indonesia multifinance KB packs"
```

**9 — Q3 bots + localization evidence**
```powershell
git add q3_native_bots/__init__.py q3_native_bots/api.py q3_native_bots/test_calls.py q3_native_bots/static/ docs/q3_localization.md docs/q3_test_calls.md docs/q3_asr_report.md data/transcripts/ph_*.json data/transcripts/id_*.json
git commit -m "Wire Taglish and Bahasa bots with native TTS and localization evidence"
```

**10 — Q4 pipeline**
```powershell
git add q4_live_nudges/__init__.py q4_live_nudges/signals.py q4_live_nudges/controls.py q4_live_nudges/pipeline.py q4_live_nudges/scenarios.py q4_live_nudges/bridge.py
git commit -m "Add real-time call insight pipeline with nudge suppression rules"
```

**11 — Q4 dashboard + latency + Q1/Q3 replay**
```powershell
git add q4_live_nudges/simulate.py q4_live_nudges/api.py q4_live_nudges/static/ docs/q4_latency.md data/recordings/live_sessions/ .gitignore
git commit -m "Add live nudge dashboard, Q1/Q3 replay and latency report"
```

**12 — App + README + remaining docs**
```powershell
git add app.py README.md docs/architecture.md docs/limitations.md docs/video_walkthrough.md
git commit -m "Serve all four questions from one app and document setup"
```

Then `git status` should be clean except the assignment PDF (optional). `git push`.
