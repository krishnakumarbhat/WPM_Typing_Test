from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LinearRegression
    from sklearn.neighbors import KNeighborsClassifier
except Exception:  # pragma: no cover
    KMeans = None
    RandomForestClassifier = None
    LinearRegression = None
    KNeighborsClassifier = None


@dataclass(slots=True)
class TrendPrediction:
    next_session_wpm: float | None
    slope: float | None


class ProgressPredictor:
    def __init__(self) -> None:
        self.model = LinearRegression() if LinearRegression else None

    def fit_predict(self, net_wpm_history: list[float]) -> TrendPrediction:
        if len(net_wpm_history) < 2 or self.model is None:
            return TrendPrediction(next_session_wpm=None, slope=None)

        x = np.arange(len(net_wpm_history), dtype=float).reshape(-1, 1)
        y = np.array(net_wpm_history, dtype=float)
        self.model.fit(x, y)
        next_idx = np.array([[len(net_wpm_history)]], dtype=float)
        pred = float(self.model.predict(next_idx)[0])
        slope = float(self.model.coef_[0])
        return TrendPrediction(next_session_wpm=round(pred, 2), slope=round(slope, 4))


class WeaknessClusterer:
    def __init__(self, n_clusters: int = 3) -> None:
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto") if KMeans else None

    def cluster(self, features: list[list[float]]) -> list[int]:
        if not features or self.model is None:
            return []
        x = np.array(features, dtype=float)
        labels = self.model.fit_predict(x)
        return labels.tolist()


class FatigueDetector:
    def __init__(self) -> None:
        self.model = RandomForestClassifier(n_estimators=100, random_state=42) if RandomForestClassifier else None

    def fit(self, features: list[list[float]], labels: list[int]) -> bool:
        if self.model is None or len(features) < 4 or len(set(labels)) < 2:
            return False
        x = np.array(features, dtype=float)
        y = np.array(labels, dtype=int)
        self.model.fit(x, y)
        return True

    def predict(self, feature_row: list[float]) -> str:
        if self.model is None:
            return "unknown"
        pred = int(self.model.predict([feature_row])[0])
        return "fatigued" if pred == 1 else "optimal"


class SkillClassifier:
    """KNN based skill tier classification."""

    def __init__(self, k: int = 5) -> None:
        self.model = KNeighborsClassifier(n_neighbors=k) if KNeighborsClassifier else None

    def fit(self, features: list[list[float]], tiers: list[str]) -> bool:
        if self.model is None or len(features) < 5 or len(set(tiers)) < 2:
            return False
        self.model.fit(features, tiers)
        return True

    def predict(self, feature_row: list[float]) -> str:
        if self.model is None:
            return "Unknown"
        return str(self.model.predict([feature_row])[0])
