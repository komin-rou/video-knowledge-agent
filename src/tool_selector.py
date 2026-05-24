from pathlib import Path


class ToolSelector:
    """
    Tool Selection Layer

    作用：
    根据当前视频是否存在字幕文件，决定使用哪种文本获取工具。
    """

    def find_subtitle_file(self, video_path: Path) -> Path | None:
        """
        查找和视频同名的字幕文件

        支持：
        .srt
        .vtt
        .ass
        """

        subtitle_extensions = [".srt", ".vtt", ".ass"]

        for ext in subtitle_extensions:
            subtitle_path = video_path.with_suffix(ext)

            if subtitle_path.exists():
                return subtitle_path

        return None

    def choose_text_extraction_tool(self, video_path: Path) -> dict:
        """
        决定使用字幕提取还是 Whisper ASR
        """

        subtitle_path = self.find_subtitle_file(video_path)

        if subtitle_path:
            return {
                "tool": "subtitle",
                "subtitle_path": subtitle_path,
                "reason": f"检测到字幕文件：{subtitle_path.name}，优先使用字幕"
            }

        return {
            "tool": "whisper",
            "subtitle_path": None,
            "reason": "未检测到字幕文件，使用 Whisper ASR"
        }