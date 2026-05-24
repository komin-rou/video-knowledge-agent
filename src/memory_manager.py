from pathlib import Path
import json
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_DIR = BASE_DIR / "data" / "memory"
MEMORY_PATH = MEMORY_DIR / "processed_videos.json"


class MemoryManager:
    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

        if not MEMORY_PATH.exists():
            self._save_memory([])

    def _load_memory(self) -> list:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_memory(self, data: list):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def is_processed(self, video_name: str) -> bool:
        memory = self._load_memory()

        for item in memory:
            if item.get("video_name") == video_name and item.get("status") == "success":
                return True

        return False

    def add_record(
        self,
        video_name: str,
        status: str,
        chunks: int = 0,

        quality_score: int = 0,

        tool_used: str = "",

        prompt_type: str = "",
        output_path: str = "",
        note: str = ""
    ):
        memory = self._load_memory()

        record = {
            "video_name": video_name,
            "status": status,
            "chunks": chunks,
            "prompt_type": prompt_type,
            "output_path": output_path,
            "note": note,
            "quality_score": quality_score,
            "tool_used": tool_used,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        memory.append(record)
        self._save_memory(memory)

        print(f"Memory 已记录：{video_name} -> {status}")