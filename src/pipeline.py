from pathlib import Path

from video_processor import extract_audio_from_video
from asr_processor import transcribe_audio
from text_cleaner import process_transcript
from knowledge_extractor import extract_knowledge

from agent_controller import VideoKnowledgeAgentController
from memory_manager import MemoryManager
from reflection_evaluator import evaluate_knowledge

from tool_selector import ToolSelector
from subtitle_processor import subtitle_to_transcript

from status_decider import decide_status_by_quality, build_status_note
from review_manager import ReviewManager
from action_logger import ActionLogger


def process_single_video(video_path: Path, need_chunking: bool, prompt_type: str):
    """
    动态执行单个视频流程：
    - 有外挂字幕：字幕转 transcript
    - 无外挂字幕：Whisper ASR
    """

    tool_selector = ToolSelector()

    print("\n[1/5] Tool Selection：选择文本获取工具")
    tool_decision = tool_selector.choose_text_extraction_tool(video_path)

    print(f"Agent 工具选择：{tool_decision['tool']}")
    print(f"选择理由：{tool_decision['reason']}")

    if tool_decision["tool"] == "subtitle":
        print("\n[2/5] 使用字幕生成 Transcript")
        transcript_path = subtitle_to_transcript(tool_decision["subtitle_path"])

    else:
        print("\n[2/5] 提取音频")
        audio_path = extract_audio_from_video(video_path)

        print("\n[3/5] Whisper ASR")
        transcript_path = transcribe_audio(audio_path)

    print("\n[4/5] 文本轻清洗")
    cleaned_path = process_transcript(transcript_path)

    print("\n[5/5] 知识提取")

    if need_chunking:
        print("Agent 决策：使用 Chunking 模式")
    else:
        print("Agent 决策：直接处理，不 Chunk")

    output_path = extract_knowledge(
        cleaned_path,
        prompt_type=prompt_type
    )

    print("\n处理完成")
    print(f"输出文件：{output_path}")

    return output_path, tool_decision["tool"]


def main():
    controller = VideoKnowledgeAgentController()
    memory = MemoryManager()
    review_manager = ReviewManager()
    logger = ActionLogger()

    decisions = controller.plan()

    if not decisions:
        print("没有找到待处理视频")
        logger.log("No pending videos found")
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
        print(f"决策理由：{decision.reason}")

        logger.log(f"Start task: {decision.video_path.name}")
        logger.log(
            f"Decision: should_process={decision.should_process}, "
            f"chunking={decision.need_chunking}, "
            f"prompt={decision.prompt_type}, "
            f"reason={decision.reason}"
        )

        if not decision.should_process:
            print("Agent 决策：跳过该视频")
            logger.log(f"Task skipped: {decision.video_path.name}, reason={decision.reason}")
            continue

        try:
            output_path, tool_used = process_single_video(
                video_path=decision.video_path,
                need_chunking=decision.need_chunking,
                prompt_type=decision.prompt_type
            )

            reflection_result = evaluate_knowledge(output_path)

            quality_score = reflection_result.get("quality_score", 0)
            quality_level = reflection_result.get("quality_level", "unknown")
            suggestion = reflection_result.get("suggestion", "")

            final_status = decide_status_by_quality(quality_score)

            note = build_status_note(
                quality_score=quality_score,
                quality_level=quality_level,
                suggestion=suggestion
            )

            if final_status in ["low_quality", "needs_review"]:
                review_manager.add_review_item(
                    video_name=decision.video_path.name,
                    quality_score=quality_score,
                    quality_level=quality_level,
                    suggestion=suggestion,
                    output_path=str(output_path)
                )

                logger.log(
                    f"Review required: video={decision.video_path.name}, "
                    f"quality_score={quality_score}, status={final_status}"
                )

            memory.add_record(
                video_name=decision.video_path.name,
                status=final_status,
                chunks=0,
                prompt_type=decision.prompt_type,
                output_path=str(output_path),
                quality_score=quality_score,
                tool_used=tool_used,
                note=note
            )

            logger.log(
                f"Task completed: video={decision.video_path.name}, "
                f"tool={tool_used}, "
                f"quality_score={quality_score}, "
                f"status={final_status}, "
                f"output={output_path}"
            )

        except Exception as e:
            print(f"处理失败：{e}")

            memory.add_record(
                video_name=decision.video_path.name,
                status="failed",
                chunks=0,
                prompt_type=decision.prompt_type,
                output_path="",
                quality_score=0,
                tool_used="unknown",
                note=str(e)
            )

            logger.log(
                f"Task failed: video={decision.video_path.name}, "
                f"error={str(e)}"
            )

    print("\n" + "=" * 60)
    print("所有任务完成")
    print("=" * 60)


if __name__ == "__main__":
    main()