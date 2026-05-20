from pathlib import Path
import json
import os

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "data" / "output"

load_dotenv(BASE_DIR / ".env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")


def build_prompt(text: str) -> str:
    """
    构造知识提取 Prompt
    """

    return f"""
你是一个专业的 AI 学习资料整理助手。

下面是一段由教学视频语音识别得到的文本，内容可能存在口语化、重复、识别错误和废话。
请你把它整理成结构化学习资料。

要求：
1. 只输出 JSON，不要输出 Markdown。
2. 不要编造原文没有的信息。
3. 如果某些字段无法确定，就使用空字符串或空列表。
4. 内容使用中文。
5. 尽量保留对学习有价值的技术概念、流程、术语和例子。

JSON 格式如下：

{{
  "title": "根据内容生成一个简洁标题",
  "summary": "用 150 字以内总结这个视频主要讲了什么",
  "main_topic": "这个视频的核心主题",
  "core_concepts": [
    {{
      "name": "核心概念名称",
      "explanation": "这个概念的简洁解释"
    }}
  ],
  "workflow": [
    "步骤1",
    "步骤2",
    "步骤3"
  ],
  "important_terms": [
    {{
      "term": "术语",
      "meaning": "含义"
    }}
  ],
  "key_points": [
    "关键知识点1",
    "关键知识点2"
  ],
  "possible_questions": [
    "适合作为复习的问题1",
    "适合作为复习的问题2"
  ],
  "raw_quality_comment": "简要评价这段 ASR 文本质量"
}}

视频文本如下：
{text}
"""


def extract_json_from_response(content: str) -> dict:
    """
    尽量从模型输出中解析 JSON
    """

    content = content.strip()

    # 防止模型包了 ```json
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("JSON 解析失败，原始输出如下：")
        print(content)
        raise e


def extract_knowledge(cleaned_text_path: Path) -> Path:
    if not DEEPSEEK_API_KEY:
        raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(cleaned_text_path, "r", encoding="utf-8") as f:
        text = f.read()

    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

    prompt = build_prompt(text)

    print(f"正在调用 DeepSeek API，模型：{DEEPSEEK_MODEL}")

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一个严谨的知识结构化助手，只输出合法 JSON。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    content = response.choices[0].message.content

    knowledge_data = extract_json_from_response(content)

    output_path = OUTPUT_DIR / f"{cleaned_text_path.stem}_knowledge.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_data, f, ensure_ascii=False, indent=2)

    print(f"知识提取完成：{output_path}")

    return output_path


def main():
    cleaned_files = list(CLEANED_DIR.glob("*_cleaned.txt"))

    if not cleaned_files:
        print("没有 cleaned 文本，请先运行 text_cleaner.py")
        return

    cleaned_text_path = cleaned_files[0]

    extract_knowledge(cleaned_text_path)


if __name__ == "__main__":
    main()