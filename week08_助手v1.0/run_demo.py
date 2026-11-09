# W8 演示记录采集脚本：真实调用助手，把原始输出与检索依据存成 JSON。
# 只做记录，不改写模型回答；answer_log.md 由这里的 JSON 人工整理而成。
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assistant_v1 import QUESTIONS, answer_details  # noqa: E402


def run_case(question, use_rag, prefer):
    try:
        record = answer_details(question, use_rag=use_rag, prefer=prefer)
        record["ok"] = True
    except Exception as error:
        record = {"question": question, "use_rag": use_rag, "requested_engine": prefer,
                  "ok": False, "error": "%s: %s" % (type(error).__name__, error)}
    return record


def main():
    parser = argparse.ArgumentParser(description="采集 W8 演示记录")
    parser.add_argument("--output", required=True, help="原始 JSON 输出路径")
    parser.add_argument("--prefer", choices=["local", "api"], default="local")
    args = parser.parse_args()

    cases = []
    # 讲义三问，RAG 模式
    for q in QUESTIONS:
        cases.append(run_case(q, use_rag=True, prefer=args.prefer))
    # 同一问题关闭 RAG，做 use_rag 开关对照
    for q in QUESTIONS:
        cases.append(run_case(q, use_rag=False, prefer=args.prefer))
    # prefer=api：未配密钥时应打印回退原因并落到本地
    cases.append(run_case(QUESTIONS[1], use_rag=True, prefer="api"))

    output = os.path.abspath(args.output)
    if os.path.exists(output):
        print("目标文件已存在，不覆盖：%s" % output)
        return 1
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as file:
        json.dump(cases, file, ensure_ascii=False, indent=2)
    print("已写入 %s（%d 条）" % (output, len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
