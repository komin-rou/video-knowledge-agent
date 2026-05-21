from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_DIR = BASE_DIR / "data" / "cleaned"
CHUNKS_DIR = BASE_DIR / "data" / "chunks"


def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """
    将长文本切分成多个 chunk

    chunk_size: 每个 chunk 的最大字符数
    overlap: 相邻 chunk 之间的重叠字符数
    """

    if chunk_size <= overlap:
        raise ValueError("chunk_size 必须大于 overlap")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def process_cleaned_text(cleaned_text_path: Path) -> list[Path]:
    """
    读取 cleaned 文本，并保存为多个 chunk 文件
    """

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    with open(cleaned_text_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_text_into_chunks(text)

    output_paths = []

    for index, chunk in enumerate(chunks, start=1):
        output_path = CHUNKS_DIR / f"{cleaned_text_path.stem}_chunk_{index:03d}.txt"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(chunk)

        output_paths.append(output_path)

    print(f"切块完成，共生成 {len(output_paths)} 个 chunks")

    return output_paths


def main():
    cleaned_files = list(CLEANED_DIR.glob("*_cleaned.txt"))

    if not cleaned_files:
        print("没有 cleaned 文本，请先运行 text_cleaner.py")
        return

    cleaned_text_path = cleaned_files[0]
    process_cleaned_text(cleaned_text_path)


if __name__ == "__main__":
    main()