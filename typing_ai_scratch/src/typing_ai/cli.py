from __future__ import annotations

import random
import sys
import time
import importlib
from datetime import datetime, timezone
from pathlib import Path

from .algorithms import LinearTypingMatcher, calculate_metrics
from .ml_models import ProgressPredictor
from .rag_pipeline import AdaptiveMemoryPipeline
from .recommender import AdaptiveRecommender
from .storage import SessionRecord, TypingRepository

try:
    readchar = importlib.import_module("readchar")
except Exception:  # pragma: no cover
    readchar = None


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "typing_ai.sqlite3"
MEMORY_DIR = ROOT / "models" / "chroma"


class TestAborted(Exception):
    pass


def load_lines(file_path: Path, fallback: list[str]) -> list[str]:
    if file_path.exists():
        return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return fallback


def choose_prompt() -> str:
    primary = load_lines(DATA_DIR / "prompts.txt", [])
    secondary = load_lines(DATA_DIR / "prompts_extra.txt", [])
    prompts = primary + secondary
    if not prompts:
        prompts = [
            "The quick brown fox jumps over the lazy dog.",
            "Practice creates progress when consistency meets focus.",
            "Type with calm rhythm and accuracy before speed.",
        ]
    return random.choice(prompts)


def _print_char_feedback(is_correct: bool, ch: str) -> None:
    green = "\033[32m"
    red = "\033[31m"
    reset = "\033[0m"
    color = green if is_correct else red
    sys.stdout.write(f"{color}{ch}{reset}")
    sys.stdout.flush()


def run_realtime_test(target_text: str) -> tuple[str, int, list[dict], float]:
    if not readchar:
        raise RuntimeError("readchar is not installed")

    matcher = LinearTypingMatcher(target_text)
    backspace_count = 0
    micro_stats: list[dict] = []

    print("\nType the target text. Press ENTER when done.\n")
    print(f"TARGET: {target_text}\n")

    start = time.perf_counter()
    last_ts = start

    while True:
        ch = readchar.readkey()
        now = time.perf_counter()
        latency_ms = (now - last_ts) * 1000
        last_ts = now

        if ch in (readchar.key.ENTER, "\n", "\r"):
            break

        if ch in (readchar.key.BACKSPACE, "\x7f", "\b"):
            matcher.backspace()
            backspace_count += 1
            sys.stdout.write("\b \b")
            sys.stdout.flush()
            continue

        state = matcher.push_char(ch)
        _print_char_feedback(state.is_correct, ch)

        micro_stats.append(
            {
                "expected_char": state.expected,
                "typed_char": state.typed,
                "latency_ms": round(latency_ms, 2),
                "index": state.index,
            }
        )

    elapsed = time.perf_counter() - start
    print("\n")
    return matcher.typed_text, backspace_count, micro_stats, elapsed


def run_line_mode_test(target_text: str) -> tuple[str, int, list[dict], float]:
    print("\n`readchar` not available. Falling back to line mode.")
    print("Paste/type the full line and press ENTER:\n")
    print(f"TARGET: {target_text}\n")

    start = time.perf_counter()
    try:
        typed_text = input("INPUT : ")
    except KeyboardInterrupt as exc:
        raise TestAborted("Typing test canceled by user") from exc
    elapsed = time.perf_counter() - start

    avg_latency = (elapsed * 1000 / len(typed_text)) if typed_text else 0.0
    micro_stats = []
    for i, typed_char in enumerate(typed_text):
        expected = target_text[i] if i < len(target_text) else ""
        micro_stats.append(
            {
                "expected_char": expected,
                "typed_char": typed_char,
                "latency_ms": round(avg_latency, 2),
                "index": i,
            }
        )
    return typed_text, 0, micro_stats, elapsed


def register_or_login(repo: TypingRepository) -> int:
    while True:
        print("\n1) Register\n2) Login")
        try:
            choice = input("Choose: ").strip()
        except KeyboardInterrupt:
            raise TestAborted("Authentication canceled by user")

        try:
            username = input("Username: ").strip()
            password = input("Password: ").strip()
        except KeyboardInterrupt:
            raise TestAborted("Authentication canceled by user")

        if choice == "1":
            try:
                user_id = repo.register(username=username, password=password)
                print(f"Registered as {username}")
                return user_id
            except Exception as exc:
                print(f"Register failed: {exc}")
        elif choice == "2":
            user_id = repo.login(username=username, password=password)
            if user_id is not None:
                print(f"Logged in as {username}")
                return user_id
            print("Login failed")
        else:
            print("Invalid option")


def run_once(user_id: int, repo: TypingRepository, recommender: AdaptiveRecommender, memory: AdaptiveMemoryPipeline) -> bool:
    target_text = choose_prompt()

    try:
        if readchar:
            typed_text, backspace_count, micro_stats, elapsed = run_realtime_test(target_text)
        else:
            typed_text, backspace_count, micro_stats, elapsed = run_line_mode_test(target_text)
    except KeyboardInterrupt:
        print("\nTest canceled. Returning to menu.")
        return False
    except TestAborted as exc:
        print(f"\n{exc}")
        return False

    matcher = LinearTypingMatcher(target_text)
    for char in typed_text:
        matcher.push_char(char)
    correct_chars, uncorrected_errors = matcher.evaluate()

    metrics = calculate_metrics(
        total_chars_typed=len(typed_text),
        correct_chars=correct_chars,
        uncorrected_errors=uncorrected_errors,
        elapsed_seconds=elapsed,
    )

    print("Results")
    print(f"- Gross WPM: {metrics.gross_wpm}")
    print(f"- Net WPM: {metrics.net_wpm}")
    print(f"- Accuracy: {metrics.accuracy_percent}%")
    print(f"- Uncorrected Errors: {metrics.uncorrected_errors}")

    record = SessionRecord(
        user_id=user_id,
        started_at=datetime.now(timezone.utc).isoformat(),
        duration_seconds=metrics.elapsed_seconds,
        target_text=target_text,
        typed_text=typed_text,
        gross_wpm=metrics.gross_wpm,
        net_wpm=metrics.net_wpm,
        accuracy=metrics.accuracy_percent,
        uncorrected_errors=metrics.uncorrected_errors,
        backspace_count=backspace_count,
        micro_stats=micro_stats,
    )
    repo.save_session(record)

    recommender.update_from_attempt(expected_text=target_text, typed_text=typed_text)
    suggestions = recommender.recommend_words(top_k=10)

    summary = (
        f"NetWPM={metrics.net_wpm}, Accuracy={metrics.accuracy_percent}, "
        f"Errors={metrics.uncorrected_errors}, TopWeakWords={[w for w, _ in suggestions[:5]]}"
    )
    memory.add_memory(user_id=user_id, summary=summary)

    print("\nAdaptive recommendations")
    if suggestions:
        print("- Words:", ", ".join([w for w, _ in suggestions[:8]]))
    else:
        print("- No weakness patterns yet. Keep practicing.")

    markov_sentence = recommender.generate_markov_sentence(max_words=10)
    print(f"- Practice sentence: {markov_sentence}")

    sessions = repo.load_user_sessions(user_id)
    predictor = ProgressPredictor()
    trend = predictor.fit_predict([float(s["net_wpm"]) for s in sessions])
    if trend.next_session_wpm is not None:
        print(f"- Predicted next Net WPM: {trend.next_session_wpm} (slope/session={trend.slope})")
    else:
        print("- Need at least 2 sessions for trend prediction.")

    return True


def build_runtime() -> tuple[TypingRepository, AdaptiveRecommender, AdaptiveMemoryPipeline]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    repo = TypingRepository(DB_PATH)

    dictionary = load_lines(
        DATA_DIR / "dictionary.txt",
        [
            "the",
            "their",
            "there",
            "receive",
            "ceiling",
            "weight",
            "practice",
            "precision",
            "typing",
            "rhythm",
            "question",
            "answer",
        ],
    )

    recommender = AdaptiveRecommender(dictionary_words=dictionary, n_values=(2, 3))
    memory = AdaptiveMemoryPipeline(persist_dir=MEMORY_DIR)
    return repo, recommender, memory


def run_cli() -> None:
    repo, recommender, memory = build_runtime()

    try:
        user_id = register_or_login(repo)
    except TestAborted as exc:
        print(f"\n{exc}")
        print("Bye")
        return

    while True:
        run_once(user_id=user_id, repo=repo, recommender=recommender, memory=memory)
        try:
            again = input("\nRun another test? (y/n): ").strip().lower()
        except KeyboardInterrupt:
            print("\nBye")
            break
        if again != "y":
            print("Bye")
            break


if __name__ == "__main__":
    run_cli()
