from pathlib import Path
from dataclasses import dataclass


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_VIDEO_DIR = BASE_DIR / "data" / "raw_videos"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"


@dataclass
class AgentDecision:
    video_path: Path
    should_process: bool
    need_chunking: bool
    prompt_type: str
    reason: str


class VideoKnowledgeAgentController:
    """
    Mini Agent Controller

    作用：
    不是直接处理视频，而是根据视频和文本情况，决定下一步怎么处理。
    这就是 Agent 的第一层：Decision Layer。
    """

    def __init__(self, chunk_threshold_chars: int = 3000):
        self.chunk_threshold_chars = chunk_threshold_chars

    def find_videos(self) -> list[Path]:
        """
        找到待处理视频
        """
        video_files = list(RAW_VIDEO_DIR.glob("*.mp4"))
        return video_files

    def estimate_video_type(self, video_path: Path) -> str:
        """
        根据文件名粗略判断视频类型

        V1 先用规则判断。
        后面可以升级成 LLM 判断。
        """

        name = video_path.stem.lower()

        if "rag" in name:
            return "rag_learning"

        if "agent" in name:
            return "agent_learning"

        if "python" in name:
            return "python_learning"

        if "recipe" in name or "food" in name or "cook" in name:
            return "recipe"

        return "general_learning"

    def choose_prompt_type(self, video_type: str) -> str:
        """
        根据视频类型选择不同的 Prompt 模板
        """

        if video_type == "recipe":
            return "recipe_prompt"

        if video_type in ["rag_learning", "agent_learning", "python_learning"]:
            return "technical_learning_prompt"

        return "general_knowledge_prompt"

    def decide_chunking(self, cleaned_text_path: Path | None) -> bool:
        """
        根据文本长度判断是否需要 chunking
        """

        if cleaned_text_path is None or not cleaned_text_path.exists():
            return True

        with open(cleaned_text_path, "r", encoding="utf-8") as f:
            text = f.read()

        return len(text) > self.chunk_threshold_chars

    def make_decision(self, video_path: Path) -> AgentDecision:
        """
        为单个视频生成处理决策
        """

        if not video_path.exists():
            return AgentDecision(
                video_path=video_path,
                should_process=False,
                need_chunking=False,
                prompt_type="none",
                reason="视频文件不存在"
            )

        video_type = self.estimate_video_type(video_path)
        prompt_type = self.choose_prompt_type(video_type)

        # V1 阶段：只要是 mp4，就先处理
        should_process = video_path.suffix.lower() == ".mp4"

        # 目前 cleaned 文本可能还没有生成，所以默认需要 chunking
        cleaned_text_path = CLEANED_DIR / f"{video_path.stem}_cleaned.txt"
        need_chunking = self.decide_chunking(cleaned_text_path)

        reason = (
            f"检测到视频类型为 {video_type}，"
            f"选择 prompt 类型为 {prompt_type}，"
            f"chunking={need_chunking}"
        )

        return AgentDecision(
            video_path=video_path,
            should_process=should_process,
            need_chunking=need_chunking,
            prompt_type=prompt_type,
            reason=reason
        )

    def plan(self) -> list[AgentDecision]:
        """
        为所有视频生成处理计划
        """

        video_files = self.find_videos()

        decisions = []

        for video_path in video_files:
            decision = self.make_decision(video_path)
            decisions.append(decision)

        return decisions


def main():
    controller = VideoKnowledgeAgentController()

    decisions = controller.plan()

    if not decisions:
        print("没有找到待处理视频")
        return

    print("=" * 60)
    print("Agent Controller 决策结果")
    print("=" * 60)

    for index, decision in enumerate(decisions, start=1):
        print(f"\n[{index}] 视频：{decision.video_path.name}")
        print(f"是否处理：{decision.should_process}")
        print(f"是否需要 chunking：{decision.need_chunking}")
        print(f"Prompt 类型：{decision.prompt_type}")
        print(f"决策理由：{decision.reason}")


if __name__ == "__main__":
    main()