# 作业 4 · smolagents 最小示例：把本周手写的 hsk_level 换成 @tool 形式，跑通 ToolCallingAgent。
# 与讲义第七节第 3 节的最小示例同构，仅三处适配本仓库：
#   1. hsk_level 读仓库根目录 weekpath.py 定位的生词表（week03_Python/data/生词表.csv）。
#   2. OpenAIModel 接本机 Ollama（OpenAI 兼容端点），本机未配置云端密钥，api_key 用本地占位——
#      真实密钥仍只放 .env，绝不写进代码。
#   3. 运行结果存 JSON 作为证据，不改写模型输出。
import argparse
import csv
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

from smolagents import tool, ToolCallingAgent, OpenAIModel  # noqa: E402

VOCAB = weekpath.data_path("生词表.csv")
LOCAL_BASE = "http://localhost:11434/v1"


@tool
def hsk_level(word: str) -> str:
    """查课程生词表里词语的 HSK 等级。

    Args:
        word: 要查询的汉字或词语
    """
    with open(VOCAB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["词汇"].strip() == word.strip():
                return "%s 是 %s 级" % (word, row["HSK等级"])
    return "未找到 %s" % word


def main():
    parser = argparse.ArgumentParser(description="smolagents 最小示例")
    parser.add_argument("--question", default="'把'字是 HSK 几级词汇？")
    parser.add_argument("--model", default="qwen2.5:1.5b")
    parser.add_argument("--output", required=True, help="证据 JSON 输出路径")
    args = parser.parse_args()

    record = {"framework": "smolagents ToolCallingAgent",
              "model": args.model, "base_url": LOCAL_BASE,
              "question": args.question, "started_at": str(datetime.datetime.now())}
    try:
        model = OpenAIModel(model_id=args.model, api_base=LOCAL_BASE, api_key="local")
        agent = ToolCallingAgent(tools=[hsk_level], model=model, max_steps=5)
        answer = agent.run(args.question)
        record["ok"] = True
        record["answer"] = str(answer)
    except Exception as error:
        record["ok"] = False
        record["error"] = "%s: %s" % (type(error).__name__, error)
    record["finished_at"] = str(datetime.datetime.now())

    output = os.path.abspath(args.output)
    if os.path.exists(output):
        print("目标文件已存在，不覆盖：%s" % output)
        return 1
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as file:
        json.dump(record, file, ensure_ascii=False, indent=2)
    print("回答：", record.get("answer") or record.get("error"))
    print("已写入", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
