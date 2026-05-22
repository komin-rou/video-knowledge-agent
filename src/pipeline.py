from pathlib import Path

from video_processor import extract_audio_from_video
from asr_processor import transcribe_audio
from text_cleaner import process_transcript
from knowledge_extractor import extract_knowledge

from agent_controller import VideoKnowledgeAgentController


def process_single_video(video_path: Path, need_chunking: bool):
    """
    动态执行单个视频流程
    """

    print("\n[1/4] 提取音频")
    audio_path = extract_audio_from_video(video_path)

    print("\n[2/4] Whisper ASR")
    transcript_path = transcribe_audio(audio_path)

    print("\n[3/4] 文本轻清洗")
    cleaned_path = process_transcript(transcript_path)

    print("\n[4/4] 知识提取")

    if need_chunking:
        print("Agent 决策：使用 Chunking 模式")

    else:
        print("Agent 决策：直接处理，不 Chunk")

    output_path = extract_knowledge(cleaned_path)

    print("\n处理完成")
    print(f"输出文件：{output_path}")


def main():
    controller = VideoKnowledgeAgentController()

    decisions = controller.plan()

    if not decisions:
        print("没有找到待处理视频")
        return

    print("=" * 60)
    print("Mini Agent 开始执行任务")
    print("=" * 60)

    for index, decision in enumerate(decisions, start=1):

        print("\n" + "=" * 60)
        print(f"任务 {index}/{len(decisions)}")
        print("=" * 60)

        print(f"视频：{decision.video_path.name}")
        print(f"是否处理：{decision.should_process}")
        print(f"Chunking：{decision.need_chunking}")
        print(f"Prompt：{decision.prompt_type}")

        if not decision.should_process:
            print("Agent 决策：跳过该视频")
            continue

        try:
            process_single_video(
                video_path=decision.video_path,
                need_chunking=decision.need_chunking
            )

        except Exception as e:
            print(f"处理失败：{e}")

    print("\n" + "=" * 60)
    print("所有任务完成")
    print("=" * 60)


if __name__ == "__main__":
    main()