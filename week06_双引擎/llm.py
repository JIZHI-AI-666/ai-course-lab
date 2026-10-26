# W6 双引擎封装：LocalEngine（Ollama）+ APIEngine（DeepSeek）+ 统一入口 LLM
# 课后作业 1 增强项：调用耗时与费用估算打印（三选一）。
# 选择理由：W7 起每次调用都要能对照「快但弱 / 慢但强 / 是否值得花 token」，
# 把耗时和示意费用打在切换日志旁边，边界测试记录才有可核对的数字，
# 也避免把空答案或静默失败误当成一次成功调用。
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

import requests  # noqa: E402
import openai  # noqa: E402


# DeepSeek 公开价量级示意（元 / 百万 token），以官网与账单为准，代码不把它当成精确计费。
API_INPUT_PRICE_PER_MILLION = 2.0
API_OUTPUT_PRICE_PER_MILLION = 8.0


class LocalEngine:
    """本地引擎：隐私任务优先、断网可用。就是 W5 的 http 直连，搬进类里。"""

    def __init__(self, model=None, base_url=None):
        self.model = model or os.getenv("LOCAL_MODEL", "qwen2.5:0.5b")
        self.base_url = (base_url or os.getenv("LOCAL_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.last_elapsed = None
        self.last_usage = None

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        session = requests.Session()
        session.trust_env = False  # 与 W5 相同：本机 11434 不走系统代理
        started = time.perf_counter()
        response = session.post(
            self.base_url + "/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        self.last_elapsed = time.perf_counter() - started
        self.last_usage = {
            "eval_count": payload.get("eval_count"),
            "prompt_eval_count": payload.get("prompt_eval_count"),
            "done_reason": payload.get("done_reason"),
        }
        return payload["message"]["content"]


class APIEngine:
    """云端引擎：复杂任务、本地失败兜底。客户端按需创建，没密钥也能纯本地跑。"""

    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.client = None
        self.last_elapsed = None
        self.last_usage = None
        self.spent = 0.0

    def _ensure_client(self):
        if self.client is None:
            key = os.getenv("DEEPSEEK_API_KEY")
            if not key or key.strip() in {"", "your_deepseek_key_here"}:
                raise RuntimeError("未配置 DEEPSEEK_API_KEY（纯本地模式请 prefer='local'）")
            self.client = openai.OpenAI(base_url=self.base_url, api_key=key, timeout=60.0)
        return self.client

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        started = time.perf_counter()
        response = self._ensure_client().chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.last_elapsed = time.perf_counter() - started
        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)
        cost = None
        if prompt_tokens is not None and completion_tokens is not None:
            cost = (
                prompt_tokens * API_INPUT_PRICE_PER_MILLION
                + completion_tokens * API_OUTPUT_PRICE_PER_MILLION
            ) / 1_000_000
            self.spent += cost
        self.last_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_yuan": cost,
            "finish_reason": response.choices[0].finish_reason,
        }
        return response.choices[0].message.content


class LLM:
    """统一入口：ask(prompt, prefer='local')。双向 try/except 回退，并打印切换原因。"""

    def __init__(self, local_model=None):
        self.local = LocalEngine(local_model)
        self.api = APIEngine()

    def _report(self, engine_name, engine, answer):
        elapsed = engine.last_elapsed
        usage = engine.last_usage or {}
        if elapsed is None:
            print("[耗时与费用] %s 未记录到耗时" % engine_name)
            return answer
        if engine_name == "local":
            print(
                "[耗时与费用] engine=local  %.2fs  本地免费  eval_count=%s  done_reason=%s"
                % (elapsed, usage.get("eval_count"), usage.get("done_reason"))
            )
        else:
            cost = usage.get("estimated_cost_yuan")
            cost_text = "未估算" if cost is None else ("约 ¥%.8f（示意单价，以账单为准）" % cost)
            print(
                "[耗时与费用] engine=api  %.2fs  prompt=%s completion=%s total=%s  %s"
                % (
                    elapsed,
                    usage.get("prompt_tokens"),
                    usage.get("completion_tokens"),
                    usage.get("total_tokens"),
                    cost_text,
                )
            )
        return answer

    def ask(self, prompt, prefer="local", **kw):
        if prefer == "local":
            first, second = self.local, self.api
            first_name, second_name = "local", "api"
            tag = "本地失败，自动切换云端"
        else:
            first, second = self.api, self.local
            first_name, second_name = "api", "local"
            tag = "云端失败，自动切换本地"
        try:
            return self._report(first_name, first, first.ask(prompt, **kw))
        except Exception as error:
            # 不吞异常、不返回空串：打印原因后再走另一侧，这就是边界测试的关键证据。
            print("[首选引擎失败，自动切换] %s" % error)
            print("[%s] %s" % (tag, error))
            return self._report(second_name, second, second.ask(prompt, **kw))


if __name__ == "__main__":
    question = "给《愚公移山》出一道 HSK4 阅读理解题，包含题干、四个选项和正确答案。"
    prefer = sys.argv[1] if len(sys.argv) > 1 else "local"
    print(LLM().ask(question, prefer=prefer))
