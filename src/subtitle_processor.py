from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_VIDEO_DIR = BASE_DIR / "data" / "raw_videos"
TRANSCRIPT_DIR = BASE_DIR / "data" / "transcripts"


def clean_subtitle_content(content: str) -> str:
    """
    清理字幕文件内容，去掉时间轴、编号、标签等
    """

    lines = content.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.isdigit():
            continue

        if "-->" in line:
            continue

        if line.upper() == "WEBVTT":
            continue

        if line.startswith("Dialogue:"):
            parts = line.split(",", maxsplit=9)
            if len(parts) == 10:
                line = parts[-1]

        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\{.*?\}", "", line)

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def subtitle_to_transcript(subtitle_path: Path) -> Path:
    """
    将字幕文件转换为 transcript txt
    """

    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    with open(subtitle_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    cleaned_text = clean_subtitle_content(content)

    output_path = TRANSCRIPT_DIR / f"{subtitle_path.stem}.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"字幕转换完成：{output_path}")

    return output_path


def main():
    subtitle_files = []

    for ext in ["*.srt", "*.vtt", "*.ass"]:
        subtitle_files.extend(RAW_VIDEO_DIR.glob(ext))

    if not subtitle_files:
        print("没有找到字幕文件")
        return

    subtitle_to_transcript(subtitle_files[0])


if __name__ == "__main__":
    main()