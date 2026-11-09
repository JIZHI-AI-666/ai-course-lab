# W8 阶段项目一：学科智能问答助手 v1.0
# 组装 = W2 提示词库 + W6 双引擎 + W7 知识库问答
# 原则：组装 ≠ 重写。本文件只做「接线」，不复制第三套模型调用代码。
import argparse
import contextlib
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  让跨周 import 生效（llm 在 week06、rag_qa 在 week07）

weekpath.load_env()

from llm import LLM  # noqa: E402
from rag_qa import retrieve, build_prompt  # noqa: E402
import rag_qa  # noqa: E402

llm = LLM()

SYSTEM_HINT = "你是国际中文教学助手，面向 HSK3–4 学习者，回答需给出依据。"

QUESTIONS = [
    "把字句的教学难点有哪些",
    "HSK4 词汇量要求是多少",
    "《愚公移山》可以设计什么课堂活动",
]


def _ensure_embed_model():
    """本机 W7 实际标签是 nomic-embed-text:w7-f16，未设置 EMBED_MODEL 时自动对齐。"""
    if os.getenv("EMBED_MODEL"):
        rag_qa.EMBED_MODEL = os.getenv("EMBED_MODEL")
        return rag_qa.EMBED_MODEL
    try:
        import requests

        session = requests.Session()
        session.trust_env = False
        names = {
            item["name"]
            for item in session.get("http://127.0.0.1:11434/api/tags", timeout=3).json().get("models", [])
        }
    except Exception:
        names = set()
    if "nomic-embed-text:w7-f16" in names:
        rag_qa.EMBED_MODEL = "nomic-embed-text:w7-f16"
    else:
        rag_qa.EMBED_MODEL = "nomic-embed-text"
    return rag_qa.EMBED_MODEL


def answer(question, use_rag=True, prefer="local"):
    """粘合层主接口。

    use_rag=True  → 先 retrieve() 拿资料、build_prompt() 拼提示词，再生成（基于资料）
    use_rag=False → 不检索，直接问答（纯对话）
    prefer        → 原样透传给 W6 的 LLM.ask()："local" 本地优先、"api" 云端优先
    """
    if use_rag:
        _ensure_embed_model()
        ctx = retrieve(question)
        prompt = SYSTEM_HINT + "\n" + build_prompt(question, ctx)
    else:
        prompt = SYSTEM_HINT + "\n" + question
    return llm.ask(prompt, prefer=prefer)


def answer_details(question, use_rag=True, prefer="local"):
    """在 answer() 之上记录实际引擎、耗时、检索依据，供演示记录留痕。

    只记录，不改变模型回答内容；实际引擎以 W6 打印的 engine= 行为准，
    因此「首选失败自动回退」也会被如实记下，而不是假装一直在用首选引擎。
    """
    started = time.perf_counter()
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        text = answer(question, use_rag=use_rag, prefer=prefer)
    logs = buffer.getvalue()
    matched = re.findall(r"engine=(local|api)", logs)
    actual_engine = matched[-1] if matched else "unknown"
    engine = llm.local if actual_engine == "local" else llm.api if actual_engine == "api" else None
    sources = []
    if use_rag:
        try:
            sources = [
                {"citation": "[S%d]" % i, "section": doc.metadata.get("section", ""),
                 "chunk_id": doc.metadata.get("chunk_id", ""), "text": doc.page_content}
                for i, doc in enumerate(rag_qa.retrieve_documents(question), 1)
            ]
        except Exception as error:  # 记录依据失败不影响主答案
            sources = [{"citation": "", "section": "", "chunk_id": "",
                        "text": "检索依据读取失败：%s" % error}]
    return {
        "question": question,
        "mode": "RAG（基于资料）" if use_rag else "纯对话",
        "use_rag": use_rag,
        "requested_engine": prefer,
        "actual_engine": actual_engine,
        "engine_switched": actual_engine != prefer,
        "model": engine.model if engine else None,
        "usage": engine.last_usage if engine else None,
        "elapsed_seconds": round(time.perf_counter() - started, 4),
        "answer": text,
        "sources": sources,
        "log": logs,
    }


def main():
    parser = argparse.ArgumentParser(description="学科智能问答助手 v1.0")
    parser.add_argument("--no-rag", action="store_true", help="关闭 RAG，走纯对话")
    parser.add_argument("--prefer", choices=["local", "api"], default="local")
    parser.add_argument("--json", action="store_true", help="输出完整原始JSON，供调试或存档")
    parser.add_argument("question", nargs="*", help="不填则跑讲义三问")
    args = parser.parse_args()
    questions = [" ".join(args.question).strip()] if args.question else QUESTIONS
    if questions == [""]:
        questions = QUESTIONS
    use_rag = not args.no_rag
    print("模式: use_rag=%s  prefer=%s  embed=%s" % (use_rag, args.prefer, _ensure_embed_model() if use_rag else "未使用"))
    records = []
    for q in questions:
        print("Q:", q)
        try:
            if args.json:
                record = answer_details(q, use_rag=use_rag, prefer=args.prefer)
                records.append(record)
                print("A:", record["answer"])
                print("实际引擎: %s  耗时: %.2fs" % (record["actual_engine"], record["elapsed_seconds"]))
            else:
                print("A:", answer(q, use_rag=use_rag, prefer=args.prefer))
        except Exception as e:
            # 常见：Ollama 没启动 / 没 pull nomic-embed-text / 没配云端密钥
            print("A: [运行失败] %s" % e)
        print("-" * 40)
    if args.json and records:
        print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
