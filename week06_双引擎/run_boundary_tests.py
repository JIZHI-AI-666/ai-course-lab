"""按讲义跑边界路径，把条件、引擎、耗时、原文日志打到 stdout。

用法：
    python run_boundary_tests.py 1          # Ollama 开，prefer=local
    python run_boundary_tests.py 3          # prefer=api
    python run_boundary_tests.py 4          # 临时去掉密钥，prefer=api → 回本地
    python run_boundary_tests.py 5          # max_tokens=15 观察截断
    python run_boundary_tests.py 2 --stop-ollama   # 关掉 Ollama 再跑 prefer=local
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

from llm import LLM  # noqa: E402

QUESTION = (
    "给《愚公移山》出一道 HSK4 阅读理解题，包含题干、四个选项和正确答案。"
    "题干必须依据愚公移山的情节，不要编造课文没有的交通事故等事实。"
)


def ollama_up() -> bool:
    try:
        import requests

        session = requests.Session()
        session.trust_env = False
        response = session.get("http://127.0.0.1:11434/api/tags", timeout=3)
        return response.ok
    except Exception:
        return False


def stop_ollama() -> None:
    subprocess.run(["killall", "Ollama"], check=False, capture_output=True)
    deadline = time.time() + 20
    while time.time() < deadline:
        if not ollama_up():
            return
        time.sleep(0.5)
    raise RuntimeError("已发送 killall Ollama，但 11434 仍可访问")


def start_ollama() -> None:
    subprocess.run(["open", "-a", "Ollama"], check=False)
    deadline = time.time() + 40
    while time.time() < deadline:
        if ollama_up():
            return
        time.sleep(0.5)
    raise RuntimeError("已执行 open -a Ollama，但 11434 仍不可访问")


def run_ask(prefer: str, **kw) -> str:
    return LLM().ask(QUESTION, prefer=prefer, **kw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("group", choices=["1", "2", "3", "4", "5"])
    parser.add_argument("--stop-ollama", action="store_true")
    args = parser.parse_args()

    print("=== 测试组 %s ===" % args.group)
    print("Ollama 当前:", "开" if ollama_up() else "关")
    print("DEEPSEEK_API_KEY:", "已配置" if os.getenv("DEEPSEEK_API_KEY") else "未配置")

    if args.group == "1":
        print("条件: Ollama 开，prefer=local")
        print(run_ask("local"))
        return 0

    if args.group == "2":
        if not args.stop_ollama:
            print("组 2 需要真实关掉 Ollama。确认后加 --stop-ollama 再跑。")
            return 2
        stopped = False
        try:
            if ollama_up():
                stop_ollama()
                stopped = True
            print("条件: Ollama 关，prefer=local（期望打印回退日志后走云端）")
            print("Ollama 当前:", "开" if ollama_up() else "关")
            print(run_ask("local"))
            return 0
        finally:
            if stopped or args.stop_ollama:
                start_ollama()
                print("已重新打开 Ollama:", "开" if ollama_up() else "关")

    if args.group == "3":
        print("条件: prefer=api（密钥有效时应直接走云端）")
        print(run_ask("api"))
        return 0

    if args.group == "4":
        print("条件: 临时清空 DEEPSEEK_API_KEY，prefer=api（期望回退本地）")
        os.environ.pop("DEEPSEEK_API_KEY", None)
        print(run_ask("api"))
        return 0

    print("条件: Ollama 开，prefer=local，max_tokens=15（观察截断）")
    print(run_ask("local", max_tokens=15, temperature=0.2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
