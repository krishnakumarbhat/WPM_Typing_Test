from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MatchState:
    index: int
    expected: str
    typed: str
    is_correct: bool


@dataclass(slots=True)
class TypingMetrics:
    total_chars_typed: int
    correct_chars: int
    uncorrected_errors: int
    elapsed_seconds: float
    gross_wpm: float
    net_wpm: float
    accuracy_percent: float


class LinearTypingMatcher:
    """Real-time index-by-index matcher using linear scanning."""

    def __init__(self, target_text: str) -> None:
        self.target_text = target_text
        self.typed_chars: list[str] = []

    @property
    def index(self) -> int:
        return len(self.typed_chars)

    @property
    def typed_text(self) -> str:
        return "".join(self.typed_chars)

    def push_char(self, char: str) -> MatchState:
        if len(char) != 1:
            raise ValueError("push_char expects exactly one character")

        i = self.index
        self.typed_chars.append(char)
        expected = self.target_text[i] if i < len(self.target_text) else ""
        return MatchState(i, expected, char, char == expected)

    def backspace(self) -> None:
        if self.typed_chars:
            self.typed_chars.pop()

    def evaluate(self) -> tuple[int, int]:
        """Return (correct_chars, uncorrected_errors)."""
        correct = 0
        errors = 0
        typed_text = self.typed_text

        for i, typed_char in enumerate(typed_text):
            expected = self.target_text[i] if i < len(self.target_text) else ""
            if typed_char == expected:
                correct += 1
            else:
                errors += 1

        return correct, errors


def calculate_metrics(
    total_chars_typed: int,
    correct_chars: int,
    uncorrected_errors: int,
    elapsed_seconds: float,
) -> TypingMetrics:
    elapsed_seconds = max(elapsed_seconds, 1e-9)
    elapsed_minutes = elapsed_seconds / 60.0

    gross_wpm = (total_chars_typed / 5.0) / elapsed_minutes
    net_wpm = gross_wpm - (uncorrected_errors / elapsed_minutes)
    accuracy = (correct_chars / total_chars_typed) * 100.0 if total_chars_typed else 0.0

    return TypingMetrics(
        total_chars_typed=total_chars_typed,
        correct_chars=correct_chars,
        uncorrected_errors=uncorrected_errors,
        elapsed_seconds=elapsed_seconds,
        gross_wpm=round(gross_wpm, 2),
        net_wpm=round(max(net_wpm, 0.0), 2),
        accuracy_percent=round(accuracy, 2),
    )
