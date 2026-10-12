"""W4 命令行学科问答机器人（API 版）。

作业功能：
1. 接收单个学科问题并调用 DeepSeek OpenAI 兼容接口。
2. 用 --batch 连续完成 3 个学科问题。
3. 用 --experiment 对比 temperature 与 max_tokens。
4. 自动记录答案、参数、token 用量和可选费用估算。

运行示例：
    python week04_API/week4_api_bot.py "把字句的教学难点有哪些"
    python week04_API/week4_api_bot.py --batch
    python week04_API/week4_api_bot.py --experiment
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

try:
    import openai  # noqa: E402
except ImportError:
    print("错误：未安装 openai。请先运行 python -m pip install -r requirements.txt。", file=sys.stderr)
    raise SystemExit(1)


BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
API_KEY_ENV = "DEEPSEEK_API_KEY"
LOG_PATH = Path(weekpath.root_path("chat_log.txt"))
REPORT_PATH = Path(weekpath.root_path("week4_实验记录.md"))

DEFAULT_QUESTION = (
    "把字句的教学难点有哪些？请从形式、语义和教学活动三个方面回答，"
    "每方面列出两点，全文不超过500字。"
)
BATCH_QUESTIONS = [
    DEFAULT_QUESTION,
    "HSK4阶段的词汇教学应重点培养哪些能力？请列出三点，并提醒我核验权威来源。",
    "请为一篇中级汉语学习者作文设计三段式评语：先肯定优点，再指出问题，最后给出修改建议。",
]
EXPERIMENTS = [
    ("temperature = 0.0", 0.0, 60),
    ("temperature = 1.5", 1.5, 60),
    ("max_tokens = 15", 0.7, 15),
    ("max_tokens = 800", 0.7, 800),
]

_client: openai.OpenAI | None = None


@dataclass
class AnswerResult:
    question: str
    answer: str
    temperature: float
    max_tokens: int
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    elapsed_seconds: float
    estimated_cost_yuan: float | None


def get_client() -> openai.OpenAI:
    """按需创建客户端，避免在导入模块时因缺少密钥直接崩溃。"""
    global _client
    if _client is None:
        key = os.getenv(API_KEY_ENV)
        if not key or key == "your_deepseek_key_here":
            raise RuntimeError(f"未配置有效的 {API_KEY_ENV}")
        _client = openai.OpenAI(base_url=BASE_URL, api_key=key, timeout=60.0)
    return _client


def estimate_cost(
    prompt_tokens: int | None,
    completion_tokens: int | None,
    input_price_per_million: float | None,
    output_price_per_million: float | None,
) -> float | None:
    """按每百万 token 单价估算费用；未提供单价时不臆测价格。"""
    if (
        prompt_tokens is None
        or completion_tokens is None
        or input_price_per_million is None
        or output_price_per_million is None
    ):
        return None
    return (
        prompt_tokens * input_price_per_million
        + completion_tokens * output_price_per_million
    ) / 1_000_000


def ask(
    question: str,
    temperature: float = 0.7,
    max_tokens: int = 800,
    input_price_per_million: float | None = None,
    output_price_per_million: float | None = None,
) -> AnswerResult:
    """发送一次请求，并返回答案、token 用量、耗时和可选费用估算。"""
    if not question.strip():
        raise ValueError("问题不能为空")
    if not 0 <= temperature <= 2:
        raise ValueError("temperature 应在 0 到 2 之间")
    if max_tokens <= 0:
        raise ValueError("max_tokens 必须大于 0")

    started = time.perf_counter()
    response = get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question.strip()}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    elapsed = time.perf_counter() - started

    answer = response.choices[0].message.content or ""
    usage = getattr(response, "usage", None)
    prompt_tokens = getattr(usage, "prompt_tokens", None)
    completion_tokens = getattr(usage, "completion_tokens", None)
    total_tokens = getattr(usage, "total_tokens", None)
    cost = estimate_cost(
        prompt_tokens,
        completion_tokens,
        input_price_per_million,
        output_price_per_million,
    )
    return AnswerResult(
        question=question.strip(),
        answer=answer.strip(),
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        elapsed_seconds=elapsed,
        estimated_cost_yuan=cost,
    )


def _display(value: Any) -> str:
    return "未返回" if value is None else str(value)


def print_result(result: AnswerResult) -> None:
    print(f"\nQ: {result.question}\nA: {result.answer}")
    print(
        "用量：输入 %s / 输出 %s / 合计 %s tokens；耗时 %.2f 秒"
        % (
            _display(result.prompt_tokens),
            _display(result.completion_tokens),
            _display(result.total_tokens),
            result.elapsed_seconds,
        )
    )
    if result.estimated_cost_yuan is not None:
        print(f"估算费用：¥{result.estimated_cost_yuan:.8f}")


def append_chat_log(result: AnswerResult, label: str = "单题") -> None:
    """把一次调用追加到根目录日志；绝不记录 API 密钥。"""
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(f"时间: {datetime.now().isoformat(timespec='seconds')}\n")
        file.write(f"模式: {label}\n")
        file.write(f"模型: {MODEL}\n")
        file.write(
            f"参数: temperature={result.temperature}, max_tokens={result.max_tokens}\n"
        )
        file.write(f"Q: {result.question}\nA: {result.answer}\n")
        file.write(
            "用量: prompt=%s, completion=%s, total=%s tokens\n"
            % (
                _display(result.prompt_tokens),
                _display(result.completion_tokens),
                _display(result.total_tokens),
            )
        )
        file.write(f"耗时: {result.elapsed_seconds:.2f} 秒\n")
        if result.estimated_cost_yuan is not None:
            file.write(f"估算费用: ¥{result.estimated_cost_yuan:.8f}\n")
        file.write("\n")


def write_experiment_report(results: list[tuple[str, AnswerResult]]) -> None:
    """写出可提交的参数体验记录，内容来自真实调用结果。"""
    lines = [
        "# Week 4 API 参数实验记录",
        "",
        f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
        f"模型：{MODEL}",
        "",
        "| 参数设置 | 输入 token | 输出 token | 耗时 秒 | 观察 |",
        "|---|---:|---:|---:|---|",
    ]
    for label, result in results:
        preview = result.answer.replace("|", "\\|").replace("\n", " ")[:100]
        lines.append(
            f"| {label} | {_display(result.prompt_tokens)} | "
            f"{_display(result.completion_tokens)} | {result.elapsed_seconds:.2f} | {preview} |"
        )
    lines.extend(
        [
            "",
            "## 我的观察",
            "",
            "- temperature 越低，表达通常越稳定、集中；越高，措辞和思路通常更发散。",
            "- max_tokens 控制最多生成长度；数值过小可能把答案截断成半句。",
            "- 模型输出可能包含事实错误，涉及等级标准和具体数字时应回查权威材料。",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def run_one(args: argparse.Namespace) -> None:
    question = " ".join(args.question).strip() or DEFAULT_QUESTION
    result = ask(
        question,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        input_price_per_million=args.input_price,
        output_price_per_million=args.output_price,
    )
    print_result(result)
    append_chat_log(result)


def run_batch(args: argparse.Namespace) -> None:
    for index, question in enumerate(BATCH_QUESTIONS, start=1):
        print(f"\n=== 学科问题 {index}/{len(BATCH_QUESTIONS)} ===")
        result = ask(
            question,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            input_price_per_million=args.input_price,
            output_price_per_million=args.output_price,
        )
        print_result(result)
        append_chat_log(result, label=f"三题批量 {index}")


def run_experiment(args: argparse.Namespace) -> None:
    question = " ".join(args.question).strip() or "用一句话说明什么是把字句。"
    results: list[tuple[str, AnswerResult]] = []
    for label, temperature, max_tokens in EXPERIMENTS:
        print(f"\n=== 参数实验：{label} ===")
        result = ask(
            question,
            temperature=temperature,
            max_tokens=max_tokens,
            input_price_per_million=args.input_price,
            output_price_per_million=args.output_price,
        )
        print_result(result)
        append_chat_log(result, label=f"参数实验 {label}")
        results.append((label, result))
    write_experiment_report(results)
    print(f"\n实验记录已写入：{REPORT_PATH}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Week 4 API 学科问答机器人")
    parser.add_argument("question", nargs="*", help="要向模型提出的问题")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--batch", action="store_true", help="运行 3 个学科问题")
    mode.add_argument("--experiment", action="store_true", help="运行 4 组参数对比")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=800)
    parser.add_argument(
        "--input-price",
        type=float,
        help="平台官网公布的输入价格，单位：元/百万 token",
    )
    parser.add_argument(
        "--output-price",
        type=float,
        help="平台官网公布的输出价格，单位：元/百万 token",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.batch:
            run_batch(args)
        elif args.experiment:
            run_experiment(args)
        else:
            run_one(args)
        return 0
    except RuntimeError as error:
        print(f"错误：{error}。", file=sys.stderr)
        print("处理：复制 .env.example 为 .env，填入自己的密钥后重试。", file=sys.stderr)
    except openai.AuthenticationError:
        print("错误：身份验证失败，请检查密钥是否有效且没有多余空格。", file=sys.stderr)
    except openai.RateLimitError:
        print("错误：请求受限或账户余额不足，请稍后重试并检查账户余额。", file=sys.stderr)
    except openai.APITimeoutError:
        print("错误：请求超时，请检查网络或减小 max_tokens。", file=sys.stderr)
    except openai.APIConnectionError:
        print("错误：无法连接 API，请检查网络和 BASE_URL。", file=sys.stderr)
    except openai.APIError as error:
        print(f"错误：API 调用失败：{error}", file=sys.stderr)
    except ValueError as error:
        print(f"错误：{error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
