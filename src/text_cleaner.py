from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent.parent

TRANSCRIPT_DIR = BASE_DIR / "data" / "transcripts"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"


def clean_text(text: str) -> str:
    """
    轻清洗：只处理格式问题，不做复杂语义清洗
    """

    # 统一换行和空白
    text = text.replace("\r", "\n")
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    # 去掉首尾空白
    text = text.strip()

    return text


def process_transcript(txt_path: Path) -> Path:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    with open(txt_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = clean_text(raw_text)

    output_path = CLEANED_DIR / f"{txt_path.stem}_cleaned.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"轻清洗完成：{output_path}")

    return output_path


def main():
    txt_files = list(TRANSCRIPT_DIR.glob("*.txt"))

    if not txt_files:
        print("没有 transcript 文件")
        return

    txt_path = txt_files[0]
    process_transcript(txt_path)


if __name__ == "__main__":
    main()