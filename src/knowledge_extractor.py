from pathlib import Path
import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from chunker import process_cleaned_text


BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "data" / "output"

load_dotenv(BASE_DIR / ".env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")


def build_chunk_prompt(chunk_text: str, chunk_index: int, total_chunks: int) -> str:
    return f"""
你是一个专业的 AI 学习资料整理助手。

下面是一个教学视频 ASR 文本的第 {chunk_index}/{total_chunks} 个片段。
文本可能有口语化、重复、识别错误和废话。

你的任务：
从这个片段中提取有学习价值的结构化知识。

要求：
1. 只输出 JSON，不要输出 Markdown。
2. 不要编造原文没有的信息。
3. 如果字段无法确定，用空字符串或空列表。
4. 内容使用中文。
5. 每个知识点尽量附带原文依据 evidence。

JSON 格式如下：

{{
  "chunk_index": {chunk_index},
  "chunk_summary": "用 80 字以内总结这个片段",
  "concepts": [
    {{
      "name": "概念名称",
      "explanation": "简洁解释",
      "evidence": "原文依据"
    }}
  ],
  "terms": [
    {{
      "term": "术语",
      "meaning": "含义",
      "evidence": "原文依据"
    }}
  ],
  "key_points": [
    {{
      "point": "关键知识点",
      "evidence": "原文依据"
    }}
  ],
  "workflow_steps": [
    {{
      "step": "流程步骤",
      "evidence": "原文依据"
    }}
  ],
  "quality_comment": "评价这个片段的 ASR 质量和知识密度"
}}

片段文本如下：
{chunk_text}
"""


def build_merge_prompt(chunk_results: list[dict]) -> str:
    chunk_results_text = json.dumps(chunk_results, ensure_ascii=False, indent=2)

    return f"""
你是一个专业的 AI 学习资料整理助手。

下面是多个视频文本片段的结构化知识提取结果。
请你将它们合并成一个完整的视频知识 JSON。

要求：
1. 只输出 JSON，不要输出 Markdown。
2. 不要编造输入中没有的信息。
3. 合并重复概念。
4. 删除明显重复或低价值内容。
5. 内容使用中文。
6. 尽量保留 evidence 字段，方便后续溯源。

最终 JSON 格式如下：

{{
  "title": "根据整体内容生成一个简洁标题",
  "summary": "用 200 字以内总结整个视频主要讲了什么",
  "main_topic": "视频核心主题",
  "core_concepts": [
    {{
      "name": "核心概念名称",
      "explanation": "简洁解释",
      "evidence": "原文依据"
    }}
  ],
  "workflow": [
    {{
      "step": "流程步骤",
      "evidence": "原文依据"
    }}
  ],
  "important_terms": [
    {{
      "term": "术语",
      "meaning": "含义",
      "evidence": "原文依据"
    }}
  ],
  "key_points": [
    {{
      "point": "关键知识点",
      "evidence": "原文依据"
    }}
  ],
  "possible_questions": [
    "适合作为复习的问题1",
    "适合作为复习的问题2"
  ],
  "raw_quality_comment": "整体评价 ASR 文本质量和知识密度"
}}

片段提取结果如下：
{chunk_results_text}
"""


def get_client() -> OpenAI:
    if not DEEPSEEK_API_KEY:
        raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件")

    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )


def parse_json_response(content: str) -> dict:
    """
    解析模型返回的 JSON 字符串
    """

    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)


def repair_json_response(client: OpenAI, broken_content: str, error_message: str) -> dict:
    """
    当模型输出的 JSON 不合法时，让模型修复 JSON
    """

    repair_prompt = f"""
下面是一段格式错误的 JSON 文本，解析时报错如下：

{error_message}

请你修复它，使其成为合法 JSON。

要求：
1. 只输出修复后的 JSON。
2. 不要输出 Markdown。
3. 不要新增字段。
4. 不要编造内容。
5. 保持原有字段和内容尽量不变。

错误 JSON 如下：
{broken_content}
"""

    print("正在尝试修复 JSON...")

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一个 JSON 修复工具，只输出合法 JSON。"
            },
            {
                "role": "user",
                "content": repair_prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    repaired_content = response.choices[0].message.content.strip()

    if repaired_content.startswith("```"):
        repaired_content = repaired_content.replace("```json", "").replace("```", "").strip()

    return json.loads(repaired_content)


def call_deepseek(client: OpenAI, prompt: str) -> dict:
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

    try:
        return parse_json_response(content)
    except json.JSONDecodeError as e:
        print("JSON 解析失败，开始修复...")
        print(f"错误信息：{e}")
        return repair_json_response(client, content, str(e))

def extract_chunk_knowledge(client: OpenAI, chunk_path: Path, chunk_index: int, total_chunks: int) -> dict:
    with open(chunk_path, "r", encoding="utf-8") as f:
        chunk_text = f.read()

    prompt = build_chunk_prompt(chunk_text, chunk_index, total_chunks)

    print(f"正在提取第 {chunk_index}/{total_chunks} 个 chunk：{chunk_path.name}")

    result = call_deepseek(client, prompt)

    time.sleep(0.5)

    return result


def merge_chunk_results(client: OpenAI, chunk_results: list[dict]) -> dict:
    print("正在合并所有 chunk 的知识结果...")

    prompt = build_merge_prompt(chunk_results)

    return call_deepseek(client, prompt)


def extract_knowledge(cleaned_text_path: Path) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    client = get_client()

    print("正在切分 cleaned 文本...")
    chunk_paths = process_cleaned_text(cleaned_text_path)

    if not chunk_paths:
        raise ValueError("没有生成任何 chunk")

    total_chunks = len(chunk_paths)
    chunk_results = []

    for index, chunk_path in enumerate(chunk_paths, start=1):
        chunk_result = extract_chunk_knowledge(
            client=client,
            chunk_path=chunk_path,
            chunk_index=index,
            total_chunks=total_chunks
        )
        chunk_results.append(chunk_result)

    final_result = merge_chunk_results(client, chunk_results)

    output_path = OUTPUT_DIR / f"{cleaned_text_path.stem}_knowledge.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

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