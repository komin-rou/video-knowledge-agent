# Video Knowledge Agent V1

一个将教学视频转换为结构化知识 JSON 的 AI 工程项目。

## Pipeline

视频文件
→ 音频提取
→ Whisper ASR 转录
→ 文本轻清洗
→ DeepSeek API 结构化知识提取
→ JSON 输出

## Project Structure

data/
src/
config/
logs/

## How to Run

1. 安装依赖
2. 配置 .env
3. 放入视频
4. 运行各模块