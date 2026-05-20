from pathlib import Path
import os
import shutil
import imageio_ffmpeg

# 获取 imageio-ffmpeg 自带的 ffmpeg
ffmpeg_path = Path(imageio_ffmpeg.get_ffmpeg_exe())
ffmpeg_dir = ffmpeg_path.parent

# Whisper 默认找 ffmpeg.exe，所以复制一份并改名
ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"

if not ffmpeg_exe.exists():
    shutil.copy(ffmpeg_path, ffmpeg_exe)

# 把 ffmpeg.exe 所在目录加入 PATH
os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ["PATH"]

import whisper


BASE_DIR = Path(__file__).resolve().parent.parent

AUDIO_DIR = BASE_DIR / "data" / "audio"
TRANSCRIPT_DIR = BASE_DIR / "data" / "transcripts"


def transcribe_audio(audio_path: Path) -> Path:
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    output_text_path = TRANSCRIPT_DIR / f"{audio_path.stem}.txt"

    print(f"当前 ffmpeg.exe 路径：{ffmpeg_exe}")
    print("正在加载 Whisper 模型...")

    model = whisper.load_model("base")

    print(f"开始转录：{audio_path.name}")

    result = model.transcribe(
        str(audio_path),
        language="zh",
        fp16=False
    )

    transcript_text = result["text"]

    with open(output_text_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    print(f"转录完成：{output_text_path}")

    return output_text_path


def main():
    audio_files = list(AUDIO_DIR.glob("*.wav"))

    if not audio_files:
        print("audio 文件夹中没有 wav 文件")
        return

    audio_path = audio_files[0]
    transcribe_audio(audio_path)


if __name__ == "__main__":
    main()