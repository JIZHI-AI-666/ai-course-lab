# W9 轨迹采集脚本：真实调用工具循环，把原始模型输出、解析结果、工具返回、最终回答存成 JSON。
# 只做记录，不改写模型输出；call_log.md 由这里的 JSON 人工整理而成。
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tool_agent  # noqa: E402


def run_case(label, question):
    record = {"label": label, "question": question, "model": tool_agent.MODEL}
    try:
        answer, steps = tool_agent.run(question)
        record["ok"] = True
        record["steps"] = steps
        record["answer"] = answer
    except Exception as error:
        record["ok"] = False
        record["error"] = "%s: %s" % (type(error).__name__, error)
    return record


def main():
    parser = argparse.ArgumentParser(description="采集 W9 调用轨迹")
    parser.add_argument("--output", required=True, help="原始 JSON 输出路径")
    args = parser.parse_args()

    cases = []
    # 轨迹 1：复合问句（编号列表式），预期模型分别点名 hsk_level 与 get_time
    cases.append(run_case("复合问句-编号列表式",
                          "请依次查询两件事：1. '把'字的 HSK 等级是多少？2. 现在的时间是多少？"))
    # 轨迹 2：单独算术题，预期点名 calc
    cases.append(run_case("算术题", "帮我算一下 35*24 等于多少"))
    # 轨迹 3：越权表达式，预期 calc 拒绝并留记录（白名单 AST 安全边界生效）
    cases.append(run_case("越权表达式被拒绝", "帮我算一下 __import__('os').getcwd() 的值"))
    # 附加：口语式复合问句（讲义第六节预告的会诊素材，观察是否答一半）
    cases.append(run_case("口语式复合问句-会诊素材", "'把'字是几级？现在几点？"))

    output = os.path.abspath(args.output)
    if os.path.exists(output):
        print("目标文件已存在，不覆盖：%s" % output)
        return 1
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as file:
        json.dump({"model": tool_agent.MODEL,
                   "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                   "cases": cases}, file, ensure_ascii=False, indent=2)
    print("已写入 %s（%d 条）" % (output, len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
