from __future__ import annotations

import random
from collections import Counter, defaultdict


def ngrams(text: str, n: int) -> list[str]:
    clean = text.lower().strip()
    if len(clean) < n:
        return []
    return [clean[i : i + n] for i in range(len(clean) - n + 1)]


class AdaptiveRecommender:
    """
    Content-based filtering over N-gram error profile.
    Word score = sum(error rates of n-grams in word).
    """

    def __init__(self, dictionary_words: list[str], n_values: tuple[int, ...] = (2, 3)) -> None:
        self.dictionary_words = [w.strip().lower() for w in dictionary_words if w.strip()]
        self.n_values = n_values
        self.attempt_counts: Counter[str] = Counter()
        self.error_counts: Counter[str] = Counter()

    def update_from_attempt(self, expected_text: str, typed_text: str) -> None:
        expected = expected_text.lower()
        typed = typed_text.lower()
        max_len = max(len(expected), len(typed))

        for n in self.n_values:
            for i in range(max_len):
                expected_ng = expected[i : i + n] if i + n <= len(expected) else ""
                typed_ng = typed[i : i + n] if i + n <= len(typed) else ""
                if len(expected_ng) == n:
                    self.attempt_counts[expected_ng] += 1
                    if typed_ng != expected_ng:
                        self.error_counts[expected_ng] += 1

    def error_profile(self) -> dict[str, float]:
        profile: dict[str, float] = {}
        for gram, attempts in self.attempt_counts.items():
            if attempts:
                profile[gram] = self.error_counts[gram] / attempts
        return profile

    def score_word(self, word: str) -> float:
        profile = self.error_profile()
        score = 0.0
        word = word.lower()
        for n in self.n_values:
            for gram in ngrams(word, n):
                score += profile.get(gram, 0.0)
        return round(score, 5)

    def recommend_words(self, top_k: int = 15) -> list[tuple[str, float]]:
        scored = [(w, self.score_word(w)) for w in self.dictionary_words]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [item for item in scored if item[1] > 0][:top_k]

    def generate_markov_sentence(self, max_words: int = 12) -> str:
        """Simple Markov chain biased by recommended words."""
        rec_words = [w for w, _ in self.recommend_words(top_k=50)]
        if not rec_words:
            return "Practice basic home-row words to build consistent speed."

        transitions: dict[str, list[str]] = defaultdict(list)
        for i in range(len(rec_words) - 1):
            transitions[rec_words[i]].append(rec_words[i + 1])

        current = random.choice(rec_words)
        sentence = [current]
        for _ in range(max_words - 1):
            options = transitions.get(current) or rec_words
            current = random.choice(options)
            sentence.append(current)

        out = " ".join(sentence)
        return out[:1].upper() + out[1:] + "."
