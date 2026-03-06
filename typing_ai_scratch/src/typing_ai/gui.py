from __future__ import annotations

import tkinter as tk
from datetime import datetime, timezone
from tkinter import messagebox, ttk

from .algorithms import LinearTypingMatcher, calculate_metrics
from .cli import build_runtime, choose_prompt
from .ml_models import ProgressPredictor
from .storage import SessionRecord


class TypingApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Typing AI Scratch")
        self.root.geometry("900x620")

        self.repo, self.recommender, self.memory = build_runtime()
        self.user_id: int | None = None

        self.target_text = ""
        self.test_start: float | None = None

        self._build_ui()
        self.new_prompt()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        auth = ttk.LabelFrame(frame, text="Login / Register", padding=10)
        auth.pack(fill="x", pady=8)

        ttk.Label(auth, text="Username").grid(row=0, column=0, sticky="w")
        self.username_var = tk.StringVar()
        ttk.Entry(auth, textvariable=self.username_var, width=24).grid(row=0, column=1, padx=8)

        ttk.Label(auth, text="Password").grid(row=0, column=2, sticky="w")
        self.password_var = tk.StringVar()
        ttk.Entry(auth, textvariable=self.password_var, width=24, show="*").grid(row=0, column=3, padx=8)

        ttk.Button(auth, text="Register", command=self.on_register).grid(row=0, column=4, padx=4)
        ttk.Button(auth, text="Login", command=self.on_login).grid(row=0, column=5, padx=4)

        self.auth_status = ttk.Label(auth, text="Not logged in")
        self.auth_status.grid(row=1, column=0, columnspan=6, sticky="w", pady=6)

        prompt_box = ttk.LabelFrame(frame, text="Target Text", padding=10)
        prompt_box.pack(fill="x", pady=8)

        self.prompt_var = tk.StringVar()
        self.prompt_label = ttk.Label(prompt_box, textvariable=self.prompt_var, wraplength=840)
        self.prompt_label.pack(anchor="w")

        action_row = ttk.Frame(prompt_box)
        action_row.pack(fill="x", pady=(10, 0))
        ttk.Button(action_row, text="New Prompt", command=self.new_prompt).pack(side="left")
        ttk.Button(action_row, text="Submit", command=self.on_submit).pack(side="left", padx=8)

        input_box = ttk.LabelFrame(frame, text="Your Input", padding=10)
        input_box.pack(fill="x", pady=8)
        self.input_text = tk.Text(input_box, height=5, wrap="word")
        self.input_text.pack(fill="x")

        feedback_box = ttk.LabelFrame(frame, text="Character Feedback", padding=10)
        feedback_box.pack(fill="both", expand=True, pady=8)
        self.feedback = tk.Text(feedback_box, height=8, wrap="word")
        self.feedback.pack(fill="both", expand=True)
        self.feedback.tag_configure("ok", foreground="green")
        self.feedback.tag_configure("bad", foreground="red")
        self.feedback.config(state="disabled")

        result_box = ttk.LabelFrame(frame, text="Results", padding=10)
        result_box.pack(fill="x", pady=8)
        self.result_var = tk.StringVar(value="Run a test to see metrics.")
        ttk.Label(result_box, textvariable=self.result_var).pack(anchor="w")

        self.recommend_var = tk.StringVar(value="")
        ttk.Label(result_box, textvariable=self.recommend_var, wraplength=840).pack(anchor="w", pady=(6, 0))

    def on_register(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing", "Username and password are required")
            return
        try:
            user_id = self.repo.register(username=username, password=password)
        except Exception as exc:
            messagebox.showerror("Register failed", str(exc))
            return

        self.user_id = user_id
        self.auth_status.config(text=f"Logged in as {username} (new account)")

    def on_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing", "Username and password are required")
            return

        user_id = self.repo.login(username=username, password=password)
        if user_id is None:
            messagebox.showerror("Login failed", "Invalid username/password")
            return

        self.user_id = user_id
        self.auth_status.config(text=f"Logged in as {username}")

    def new_prompt(self) -> None:
        self.target_text = choose_prompt()
        self.prompt_var.set(self.target_text)
        self.input_text.delete("1.0", "end")
        self._set_feedback("", [])
        self.result_var.set("Typing started. Press Submit when done.")
        self.recommend_var.set("")
        self.test_start = datetime.now(timezone.utc).timestamp()

    def _set_feedback(self, text: str, tags: list[str]) -> None:
        self.feedback.config(state="normal")
        self.feedback.delete("1.0", "end")
        for ch, tag in zip(text, tags):
            self.feedback.insert("end", ch, tag)
        self.feedback.config(state="disabled")

    def on_submit(self) -> None:
        if self.user_id is None:
            messagebox.showwarning("Not logged in", "Please register or login first")
            return

        typed = self.input_text.get("1.0", "end").rstrip("\n")
        if self.test_start is None:
            self.new_prompt()

        start_ts = self.test_start or datetime.now(timezone.utc).timestamp()
        elapsed = max(datetime.now(timezone.utc).timestamp() - start_ts, 0.001)

        matcher = LinearTypingMatcher(self.target_text)
        feedback_tags: list[str] = []
        for ch in typed:
            state = matcher.push_char(ch)
            feedback_tags.append("ok" if state.is_correct else "bad")

        correct_chars, uncorrected_errors = matcher.evaluate()
        metrics = calculate_metrics(
            total_chars_typed=len(typed),
            correct_chars=correct_chars,
            uncorrected_errors=uncorrected_errors,
            elapsed_seconds=elapsed,
        )

        avg_latency = (elapsed * 1000 / len(typed)) if typed else 0.0
        micro_stats = []
        for i, typed_char in enumerate(typed):
            expected = self.target_text[i] if i < len(self.target_text) else ""
            micro_stats.append(
                {
                    "expected_char": expected,
                    "typed_char": typed_char,
                    "latency_ms": round(avg_latency, 2),
                    "index": i,
                }
            )

        record = SessionRecord(
            user_id=self.user_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            duration_seconds=metrics.elapsed_seconds,
            target_text=self.target_text,
            typed_text=typed,
            gross_wpm=metrics.gross_wpm,
            net_wpm=metrics.net_wpm,
            accuracy=metrics.accuracy_percent,
            uncorrected_errors=metrics.uncorrected_errors,
            backspace_count=0,
            micro_stats=micro_stats,
        )
        self.repo.save_session(record)

        self.recommender.update_from_attempt(expected_text=self.target_text, typed_text=typed)
        suggestions = self.recommender.recommend_words(top_k=8)

        summary = (
            f"NetWPM={metrics.net_wpm}, Accuracy={metrics.accuracy_percent}, "
            f"Errors={metrics.uncorrected_errors}, TopWeakWords={[w for w, _ in suggestions[:5]]}"
        )
        self.memory.add_memory(user_id=self.user_id, summary=summary)

        sessions = self.repo.load_user_sessions(self.user_id)
        predictor = ProgressPredictor()
        trend = predictor.fit_predict([float(s["net_wpm"]) for s in sessions])

        self._set_feedback(typed, feedback_tags)

        trend_text = (
            f"Predicted next Net WPM: {trend.next_session_wpm}"
            if trend.next_session_wpm is not None
            else "Need at least 2 sessions for trend prediction"
        )
        self.result_var.set(
            f"Gross WPM: {metrics.gross_wpm} | Net WPM: {metrics.net_wpm} | "
            f"Accuracy: {metrics.accuracy_percent}% | Errors: {metrics.uncorrected_errors} | {trend_text}"
        )

        if suggestions:
            words = ", ".join([w for w, _ in suggestions])
            sentence = self.recommender.generate_markov_sentence(max_words=10)
            self.recommend_var.set(f"Recommendations: {words} | Practice sentence: {sentence}")
        else:
            self.recommend_var.set("No weakness patterns yet. Keep practicing.")


def run_gui() -> None:
    root = tk.Tk()
    TypingApp(root)
    root.mainloop()
