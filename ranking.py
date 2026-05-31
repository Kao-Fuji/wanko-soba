
# ranking.py
# 本番モードのスコアを保存・読み込みするファイルです。

import json
from pathlib import Path
from datetime import datetime

from setting import RANKING_FILE


class RankingManager:
    def __init__(self):
        self.path = Path(__file__).parent / RANKING_FILE

    def load(self):
        if not self.path.exists():
            return []

        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

        except Exception:
            pass

        return []

    def save_all(self, data):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_score(self, score, mode="本番"):
        data = self.load()

        data.append({
            "score": int(score),
            "mode": mode,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        data.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.save_all(data)

        return self.get_rank(score, data), len(data)

    def get_rank(self, score, data=None):
        if data is None:
            data = self.load()

        sorted_scores = sorted(
            [d.get("score", 0) for d in data],
            reverse=True
        )

        for index, saved_score in enumerate(sorted_scores, start=1):
            if int(score) >= int(saved_score):
                return index

        return len(sorted_scores) + 1

    def top(self, limit=10):
        data = self.load()
        data.sort(key=lambda x: x.get("score", 0), reverse=True)
        return data[:limit]