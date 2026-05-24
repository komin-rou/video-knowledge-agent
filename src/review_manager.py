from pathlib import Path
import json
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

REVIEW_DIR = BASE_DIR / "data" / "review"
REVIEW_PATH = REVIEW_DIR / "review_queue.json"


class ReviewManager:
    def __init__(self):
        REVIEW_DIR.mkdir(parents=True, exist_ok=True)

        if not REVIEW_PATH.exists():
            self._save([])

    def _load(self) -> list:
        with open(REVIEW_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: list):
        with open(REVIEW_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_review_item(
        self,
        video_name: str,
        quality_score: int,
        quality_level: str,
        suggestion: str,
        output_path: str
    ):
        data = self._load()

        item = {
            "video_name": video_name,
            "quality_score": quality_score,
            "quality_level": quality_level,
            "suggestion": suggestion,
            "output_path": output_path,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        data.append(item)
        self._save(data)

        print(f"Review Queue 已添加：{video_name}")