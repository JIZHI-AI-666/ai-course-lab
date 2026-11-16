# W9 手写最小工具调用循环（不用框架）
# 依赖：pip install openai python-dotenv
#
# 与课程骨架 week09_工具调用/tool_agent.py 同构，仅两处适配本仓库：
#   1. 数据路径复用根目录 weekpath.py —— 生词表在 week03_Python/data/生词表.csv，第 3 周起就是同一份。
#   2. 本机 Ollama 演示时自动放开对 localhost 的代理拦截（对应讲义 demo_w9_local.bat 处理的问题）。
#      云端口径不变：配好 .env 的 DEEPSEEK_API_KEY 后不设 BASE_URL/MODEL 即走 deepseek-chat。
import os
import csv
import sys
import ast
import json
import re
import operator
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  数据路径 + 加载 .env

weekpath.load_env()

import openai  # noqa: E402

VOCAB = weekpath.data_path("生词表.csv")
W9_DATA = weekpath.root_path("week09_工具调用", "data")

# 默认走 DeepSeek 云端；本机演示可通过环境变量切到 Ollama（OpenAI 兼容端点），例如：
#   DEEPSEEK_BASE_URL=http://localhost:11434/v1
#   DEEPSEEK_MODEL=qwen2.5:1.5b
# 不设置时行为与云端口径完全一致。
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

_client = None


def get_client():
    global _client
    if _client is None:
        base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        if "localhost" in base or "127.0.0.1" in base:
            # 系统代理会拦截对 localhost 的请求（Ollama 报 APIConnectionError），
            # 讲义 demo_w9_local.bat 同样处理过这个问题；只对本地端点放开，不影响云端。
            no_proxy = "localhost,127.0.0.1"
            os.environ.setdefault("NO_PROXY", no_proxy)
            os.environ.setdefault("no_proxy", no_proxy)
            api_key = "local"  # 本地端点不校验密钥；真实密钥仍只从 .env 读，绝不写进代码
        else:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise RuntimeError("未配置 DEEPSEEK_API_KEY，请先在 .env 中填写")
        _client = openai.OpenAI(base_url=base, api_key=api_key)
    return _client


def get_time():
    return str(datetime.datetime.now())


# ---- 安全计算：白名单 AST，绝不使用裸 eval ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("只允许数字与 + - * / ** % 运算")


def calc(expr):
    """教学演示用：只做四则运算。为什么不用 eval？
    因为 eval 会执行任意 Python 代码，是典型的安全反模式（本课程伦理红线之一）。"""
    try:
        return str(_eval_node(ast.parse(str(expr), mode="eval")))
    except ZeroDivisionError:
        return "错误：除数为 0"
    except Exception as e:
        return "拒绝计算：%s" % e


def hsk_level(word):
    with open(VOCAB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["词汇"].strip() == str(word).strip():
                return "%s 是 %s 级" % (word, row["HSK等级"])
    return "未找到 %s" % word


# ---- 作业 2 · 第 4 个工具：课文难度评估 ----
def text_difficulty(source, target_level):
    """评估课文对目标 HSK 等级学生的难度。

    source：课文原文，或 W9 数据目录下的课文文件名（如 '愚公移山'，读 愚公移山.txt）；
    target_level：目标等级，1-9 的整数。
    口径：只统计课程生词表（week03_Python/data/生词表.csv）收录且在课文中出现的词，
    不做全文分词——生词表外的词不参与统计，这是本工具的已知边界，如实写进返回值。
    覆盖率 = 出现词汇中等级不超过目标的占比；等级高于目标的列入超纲词。"""
    try:
        level = int(target_level)
    except (TypeError, ValueError):
        return "拒绝评估：目标等级必须是 1-9 的整数，收到 %r" % (target_level,)
    if not 1 <= level <= 9:
        return "拒绝评估：目标等级超出 1-9，收到 %d" % level
    text = str(source)
    candidate = os.path.join(W9_DATA, "%s.txt" % str(source).strip())
    if os.path.isfile(candidate):
        with open(candidate, encoding="utf-8") as f:
            text = f.read()
    if not text.strip():
        return "拒绝评估：课文为空"
    covered, beyond = [], []
    with open(VOCAB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            word = row["词汇"].strip()
            if word and word in text:
                (covered if int(row["HSK等级"]) <= level else beyond).append(
                    "%s(%s级)" % (word, row["HSK等级"]))
    found = len(covered) + len(beyond)
    if not found:
        return "课文 %d 字：生词表词汇在课文中一个都没出现，覆盖率无法统计。" % len(text)
    rate = len(covered) / found * 100
    result = ("课文 %d 字，目标 HSK%d。生词表词汇出现 %d 个，"
              "其中不超过 %d 级的 %d 个，覆盖率 %.1f%%；"
              % (len(text), level, found, level, len(covered), rate))
    if beyond:
        result += "超纲词 %d 个：%s。" % (len(beyond), "、".join(sorted(beyond)))
    else:
        result += "无超纲词。"
    result += "（口径：仅统计生词表收录词汇，生词表外词汇未参与统计）"
    return result


TOOLS = {"get_time": get_time, "calc": calc, "hsk_level": hsk_level,
         "text_difficulty": text_difficulty}

# 回喂文案：骨架原文案是「工具返回：{结果}。请据此作答。」。
# 作业 2 实测（1.5B 小模型，5 连跑复现）：工具返回较长（如 text_difficulty 的评估报告）时，
# 原文案下模型 5/5 复读调用直到 max_calls 收口；把「结果已是最终数据、请直接作答」写明后 5/5 正常作答。
# 对照实验数据见 evidence/homework1_failures_20261116.json 与作业文档。
FEED_TEMPLATE = ("工具返回（这是全部工具结果，已经是最终数据）：\n%s\n"
                 "请直接依据以上结果用中文回答用户的问题，不要再输出任何调用 JSON。")

SYS = ("你是国际中文助教。可用工具只有这 4 个：get_time（查当前时间，无参数）、"
       "calc（四则运算，如 calc('35*24')）、hsk_level（查生词 HSK 等级，如 hsk_level('把')）、"
       "text_difficulty（课文难度评估：输入课文原文或课文文件名 + 目标等级数字，"
       "如 text_difficulty('愚公移山', 4)）。"
       '如需调用，只输出一行 JSON，格式：{"tool": "工具名", "args": [参数]}；'
       "一次只调用一个工具，绝不编造不存在的工具名；无需工具时直接回答。")


def parse_calls(txt):
    """容错解析：剥掉 ```json 围栏与前后客套话，返回全部工具调用（0/1/多个）。

    模型不一定老实输出一个 JSON：可能带围栏、可能一段自然语言里夹着 JSON、
    也可能把多个工具调用并列输出成多行——这里全部兜住。"""
    s = (txt or "").strip()
    s = s.replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
        return [obj] if isinstance(obj, dict) else []
    except Exception:
        m = re.search(r"\{.*\}", s, re.S)  # re.S：跨行也能匹配到 JSON 块
        if m:
            try:
                obj = json.loads(m.group())
                if isinstance(obj, dict):
                    return [obj]
            except Exception:
                pass
        # 多个工具调用并列输出（小模型常态）：逐块全部解析，一轮依次执行
        calls = []
        for blk in re.findall(r"\{[^{}]*\}", s):
            try:
                obj = json.loads(blk)
            except Exception:
                continue
            if isinstance(obj, dict):
                calls.append(obj)
        return calls


def run(user_msg, max_calls=2):
    """最小循环：决定 → 执行 → 回喂 → 再生成。返回 (最终回答, 轨迹步骤列表)。"""
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user_msg}]
    steps = []
    for _ in range(max_calls):
        txt = get_client().chat.completions.create(
            model=MODEL, messages=msgs).choices[0].message.content
        calls = [c for c in parse_calls(txt)
                 if isinstance(c.get("tool"), str) and c.get("tool") in TOOLS]
        steps.append({"model_output": txt, "parsed_calls": calls})
        if not calls:
            return txt, steps                                 # 没调用工具 → 直接回答
        # 一轮内依次执行模型请求的全部工具，结果合并回喂
        results = []
        for call in calls:
            args = call.get("args") or []
            if not isinstance(args, list):
                results.append("工具参数格式错误：%r" % (args,))
                continue
            try:
                result = TOOLS[call["tool"]](*args)
                results.append("%s%r → %s" % (call["tool"], args, result))
                steps.append({"tool": call["tool"], "args": args, "result": result})
            except Exception as e:
                results.append("工具执行失败：%s" % e)
                steps.append({"tool": call["tool"], "args": args, "error": str(e)})
        msgs += [{"role": "assistant", "content": txt},
                 {"role": "user", "content": FEED_TEMPLATE % "；".join(results)}]
    # 达到上限后强制收口，避免无限循环烧 token
    txt = get_client().chat.completions.create(
        model=MODEL, messages=msgs).choices[0].message.content
    steps.append({"model_output": txt, "parsed_calls": [], "note": "max_calls 到顶强制收口"})
    return txt, steps


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "请依次查询两件事：1. '把'字的 HSK 等级是多少？2. 现在的时间是多少？"
    print("用户输入：", q)
    answer, _ = run(q)
    print("助手：", answer)
