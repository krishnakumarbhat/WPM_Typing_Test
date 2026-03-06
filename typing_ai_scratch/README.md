# Typing AI Scratch (New clean implementation)

This folder is a fresh, working typing test project built from scratch with:
- Linear scan (two-pointer/index) real-time string matching
- Standard typing formulas (Gross WPM, Net WPM, Accuracy)
- SQLite login + session storage
- Adaptive recommender (N-gram error profile + content-based filtering)
- Markov-chain sentence generation for targeted practice
- Optional ML/RAG stack integration with LangGraph + LlamaIndex + ChromaDB

## 1) Core Algorithms

### Real-time matching (linear scan)
For each typed index `i`:
- Correct if `typed_text[i] == target_text[i]`
- Incorrect otherwise
- Backspace removes last typed char and decrements effective index

Implemented in: `src/typing_ai/algorithms.py` (`LinearTypingMatcher`).

### WPM formulas
Using typing-test standard: `1 word = 5 characters`.

- Gross WPM:

$$
\text{Gross WPM} = \frac{(\text{Total Characters Typed}/5)}{\text{Time in Minutes}}
$$

- Net WPM:

$$
\text{Net WPM} = \text{Gross WPM} - \frac{\text{Uncorrected Errors}}{\text{Time in Minutes}}
$$

### Accuracy formula

$$
\text{Accuracy (\%)} = \left(\frac{\text{Correct Characters}}{\text{Total Characters Typed}}\right) \times 100
$$

## 2) ML Approach Included

Implemented modules:
- `src/typing_ai/ml_models.py`
  - `ProgressPredictor` (Linear Regression)
  - `WeaknessClusterer` (K-Means)
  - `FatigueDetector` (RandomForest classifier)
  - `SkillClassifier` (KNN)
- `src/typing_ai/recommender.py`
  - N-gram error tracking + word scoring
  - Markov sentence generation biased by weak patterns

Word scoring formula used:

$$
\text{Word Score} = \sum (\text{Error Rate of N-grams in the word})
$$

## 3) Data Pipeline

Session data stored in SQLite (`data/typing_ai.sqlite3`):
- User auth: username + password hash
- Session metadata: timestamp, duration
- Macro stats: gross_wpm, net_wpm, accuracy, errors
- Micro stats: per-key `[expected_char, typed_char, latency_ms, index]`

## 4) LangGraph / LlamaIndex / ChromaDB

`src/typing_ai/rag_pipeline.py` provides:
- ChromaDB persistent memory store
- Minimal LangGraph retrieve→recommend workflow
- LlamaIndex builder for indexed text memories

If these packages are not installed, the app still runs with graceful fallback.

## 5) Run

From this folder:

```bash
python3 -m pip install -r requirements.txt
python3 main.py --cli
```

GUI mode:

```bash
python3 main.py --gui
```

Notes:
- If `readchar` is installed, you get key-by-key real-time feedback in terminal.
- If not installed, it falls back to line mode.
- `Ctrl+C` is handled gracefully in CLI mode (no traceback spam).

## 6) Project Layout

- `main.py` – entry point
- `src/typing_ai/algorithms.py` – matching + metrics
- `src/typing_ai/storage.py` – SQLite login/session repository
- `src/typing_ai/recommender.py` – adaptive recommender + Markov practice sentence
- `src/typing_ai/ml_models.py` – ML utilities
- `src/typing_ai/rag_pipeline.py` – LangGraph/LlamaIndex/ChromaDB integration
- `data/prompts.txt` – typing prompts
- `data/prompts_extra.txt` – larger prompt database
- `data/dictionary.txt` – recommendation dictionary
