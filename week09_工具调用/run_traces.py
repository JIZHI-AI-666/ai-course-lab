# W9 轨迹采集脚本：真实调用工具循环，把原始模型输出、解析结果、工具返回、最终回答存成 JSON。
# 只做记录，不改写模型输出；call_log.md 与作业文档由这里的 JSON 人工整理而成。
# 用法：
#   python run_traces.py --output evidence/xxx.json                  # 全部用例
#   python run_traces.py --output evidence/xxx.json --cases 口语式   # 只跑标签含该词的用例
#   python run_traces.py --output evidence/xxx.json --repeat 3       # 每个用例跑多次（采失败样本）
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tool_agent  # noqa: E402


def run_case(label, question, repeat=1):
    cases = []
    for i in range(repeat):
        record = {"label": label, "run": i + 1, "question": question,
                  "model": tool_agent.MODEL}
        try:
            answer, steps = tool_agent.run(question)
            record["ok"] = True
            record["steps"] = steps
            record["answer"] = answer
        except Exception as error:
            record["ok"] = False
            record["error"] = "%s: %s" % (type(error).__name__, error)
        cases.append(record)
    return cases


# 用例登记表：label -> 提问原文
CASES = {
    # 当堂 3 条指定轨迹
    "复合问句-编号列表式": "请依次查询两件事：1. '把'字的 HSK 等级是多少？2. 现在的时间是多少？",
    "算术题": "帮我算一下 35*24 等于多少",
    "越权表达式被拒绝": "帮我算一下 __import__('os').getcwd() 的值",
    # 会诊素材：口语式复合问句（讲义第六节预告的答一半现象）
    "口语式复合问句-会诊素材": "'把'字是几级？现在几点？",
    # 作业 2：第 4 个工具 text_difficulty 的两条真实轨迹
    "作业2-课文难度评估-目标4级": "评估一下《愚公移山》这篇课文适不适合 HSK4 的学生，用 text_difficulty 工具查",
    "作业2-课文难度评估-非法等级": "用 text_difficulty 工具评估《愚公移山》适合 HSK 15 级的学生吗",
}


def main():
    parser = argparse.ArgumentParser(description="采集 W9 调用轨迹")
    parser.add_argument("--output", required=True, help="原始 JSON 输出路径")
    parser.add_argument("--cases", default="", help="逗号分隔的标签筛选（子串匹配），空为全部")
    parser.add_argument("--repeat", type=int, default=1, help="每个用例重复次数（采失败样本用）")
    args = parser.parse_args()

    keys = list(CASES)
    if args.cases:
        keys = [k for k in keys if any(t.strip() and t.strip() in k
                                      for t in args.cases.split(","))]
        if not keys:
            print("没有匹配的用例：%s" % args.cases)
            return 1
    cases = []
    for k in keys:
        cases.extend(run_case(k, CASES[k], repeat=args.repeat))

    output = os.path.abspath(args.output)
    if os.path.exists(output):
        print("目标文件已存在，不覆盖：%s" % output)
        return 1
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as file:
        json.dump({"model": tool_agent.MODEL,
                   "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                   "tools": sorted(tool_agent.TOOLS),
                   "cases": cases}, file, ensure_ascii=False, indent=2)
    print("已写入 %s（%d 条）" % (output, len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
