from pathlib import Path
from moviepy import VideoFileClip


# 项目根目录：Video_Knowledge_V1
BASE_DIR = Path(__file__).resolve().parent.parent

# 原视频目录
RAW_VIDEO_DIR = BASE_DIR / "data" / "raw_videos"

# 音频输出目录
AUDIO_DIR = BASE_DIR / "data" / "audio"


def extract_audio_from_video(video_path: Path) -> Path:
    """
    从视频文件中提取音频，并保存为 wav 文件
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    output_audio_path = AUDIO_DIR / f"{video_path.stem}.wav"

    print(f"正在处理视频：{video_path.name}")

    video = VideoFileClip(str(video_path))

    if video.audio is None:
        raise ValueError("这个视频没有音频轨道")

    video.audio.write_audiofile(str(output_audio_path))

    video.close()

    print(f"音频提取完成：{output_audio_path}")

    return output_audio_path


def main():
    video_files = list(RAW_VIDEO_DIR.glob("*.mp4"))

    if not video_files:
        print("没有找到 mp4 视频，请先把视频放到 data/raw_videos/ 目录下")
        return

    # V1 先只处理第一个视频
    video_path = video_files[0]

    extract_audio_from_video(video_path)


if __name__ == "__main__":
    main()