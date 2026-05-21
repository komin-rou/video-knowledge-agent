from pathlib import Path

from video_processor import extract_audio_from_video
from asr_processor import transcribe_audio
from text_cleaner import process_transcript
from knowledge_extractor import extract_knowledge


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_VIDEO_DIR = BASE_DIR / "data" / "raw_videos"


def run_pipeline(video_path: Path):
    """
    单个视频完整流程：
    视频 -> 音频 -> ASR文本 -> 清洗文本 -> 结构化知识JSON
    """

    print("=" * 60)
    print(f"开始处理视频：{video_path.name}")
    print("=" * 60)

    try:
        print("\n[1/4] 提取音频")
        audio_path = extract_audio_from_video(video_path)

        print("\n[2/4] 语音识别")
        transcript_path = transcribe_audio(audio_path)

        print("\n[3/4] 文本轻清洗")
        cleaned_path = process_transcript(transcript_path)

        print("\n[4/4] LLM 知识结构化")
        output_json_path = extract_knowledge(cleaned_path)

        print("\n处理完成")
        print(f"最终输出文件：{output_json_path}")

    except Exception as e:
        print(f"\n处理失败：{video_path.name}")
        print(f"错误信息：{e}")


def main():
    video_files = list(RAW_VIDEO_DIR.glob("*.mp4"))

    if not video_files:
        print("没有找到视频文件，请把 mp4 放到 data/raw_videos/ 目录下")
        return

    print(f"共找到 {len(video_files)} 个视频文件")

    for index, video_path in enumerate(video_files, start=1):
        print(f"\n正在处理第 {index}/{len(video_files)} 个视频")
        run_pipeline(video_path)

    print("\n所有视频处理完成")


if __name__ == "__main__":
    main()