"""不访问网络的 Week 4 核心逻辑测试。"""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeOpenAIError(Exception):
    pass


# 让测试环境在未安装第三方 SDK 时也能导入模块；真实运行仍使用 requirements.txt。
if "openai" not in sys.modules:
    sys.modules["openai"] = types.SimpleNamespace(
        OpenAI=object,
        AuthenticationError=FakeOpenAIError,
        RateLimitError=FakeOpenAIError,
        APITimeoutError=FakeOpenAIError,
        APIConnectionError=FakeOpenAIError,
        APIError=FakeOpenAIError,
    )


MODULE_PATH = Path(__file__).with_name("week4_api_bot.py")
SPEC = importlib.util.spec_from_file_location("week4_api_bot", MODULE_PATH)
assert SPEC and SPEC.loader
BOT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BOT
SPEC.loader.exec_module(BOT)


class FakeCompletions:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return types.SimpleNamespace(
            choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="测试答案"))],
            usage=types.SimpleNamespace(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=30,
            ),
        )


class FakeClient:
    def __init__(self):
        self.completions = FakeCompletions()
        self.chat = types.SimpleNamespace(completions=self.completions)


class Week4BotTests(unittest.TestCase):
    def test_cost_formula(self):
        value = BOT.estimate_cost(1000, 2000, 2.0, 3.0)
        self.assertAlmostEqual(value, 0.008)

    def test_missing_prices_do_not_guess(self):
        self.assertIsNone(BOT.estimate_cost(10, 20, None, None))

    def test_ask_collects_answer_and_usage(self):
        fake = FakeClient()
        with patch.object(BOT, "get_client", return_value=fake):
            result = BOT.ask("测试问题", temperature=0.2, max_tokens=40)
        self.assertEqual(result.answer, "测试答案")
        self.assertEqual(result.total_tokens, 30)
        self.assertEqual(fake.completions.kwargs["temperature"], 0.2)
        self.assertEqual(fake.completions.kwargs["max_tokens"], 40)

    def test_question_must_not_be_empty(self):
        with self.assertRaises(ValueError):
            BOT.ask("   ")


if __name__ == "__main__":
    unittest.main()
