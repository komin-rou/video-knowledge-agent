from pathlib import Path
import json
import os

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")


def build_evaluation_prompt(knowledge_data: dict) -> str:
    return f"""
你是一个严谨的知识质量评估助手。

下面是一份从视频中提取出来的结构化知识 JSON。
请你评估它的质量。

评估维度：
1. 信息完整度
2. 概念清晰度
3. 是否有明显幻觉
4. evidence 是否有效
5. 是否适合作为知识库数据

只输出 JSON，不要输出 Markdown。

JSON 格式如下：

{{
  "quality_score": 0到100之间的整数,
  "quality_level": "low / medium / high",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["问题1", "问题2"],
  "suggestion": "下一步改进建议"
}}

待评估数据如下：
{json.dumps(knowledge_data, ensure_ascii=False, indent=2)}
"""


def get_client() -> OpenAI:
    if not DEEPSEEK_API_KEY:
        raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件")

    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )


def evaluate_knowledge(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        knowledge_data = json.load(f)

    client = get_client()

    prompt = build_evaluation_prompt(knowledge_data)

    print("正在进行 Agent Reflection：评估知识质量...")

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一个知识质量评估助手，只输出合法 JSON。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    result = json.loads(content)

    print(f"Reflection 完成，质量评分：{result.get('quality_score')}")

    return result


def main():
    output_dir = BASE_DIR / "data" / "output"
    json_files = list(output_dir.glob("*_knowledge.json"))

    if not json_files:
        print("没有找到 knowledge JSON")
        return

    result = evaluate_knowledge(json_files[0])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()