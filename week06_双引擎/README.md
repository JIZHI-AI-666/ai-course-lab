# 第六周：双引擎封装

把 W5 的本地 Ollama 调用和 W4 的 DeepSeek 调用收成同一个入口：`from llm import LLM`。调用方只传 `prompt` 和 `prefer`，不必每次改地址和返回字段。

## 文件

| 文件 | 作用 |
|---|---|
| `llm.py` | `LocalEngine` + `APIEngine` + `LLM.ask(prompt, prefer="local")` |
| `run_boundary_tests.py` | 五组边界路径的实测入口 |
| `week06_test_log.md` | 边界测试记录（含回退日志原文） |
| `学科文本_预习RAG.md` | 课后作业 3：下周 RAG 用的学科文本 |

课后作业 1 的增强项写在 `llm.py` 文件头：打印调用耗时，云端附带 token 与示意费用。

## 本机准备

```bash
python3 -m pip install -r week06_双引擎/requirements.txt
cp .env.example .env   # 只在本机填写 DEEPSEEK_API_KEY，不要提交
```

本地模型默认 `qwen2.5:0.5b`，可用环境变量 `LOCAL_MODEL` 覆盖。

## 课堂三条路径

同一道学科题：给《愚公移山》出一道 HSK4 阅读理解题。

```bash
# ① 正常本地
python week06_双引擎/run_boundary_tests.py 1

# ② 关掉 Ollama 再跑 prefer=local（会打印回退日志，测完自动重新打开 Ollama）
python week06_双引擎/run_boundary_tests.py 2 --stop-ollama

# ③ 直接走云端
python week06_双引擎/run_boundary_tests.py 3

# ④ 云端不可用（临时去掉密钥）prefer=api → 回本地
python week06_双引擎/run_boundary_tests.py 4

# ⑤ max_tokens=15 观察截断
python week06_双引擎/run_boundary_tests.py 5
```

2026-10-26 已补跑路径 ②、③：本地失败后云端作答与直接云端作答均成功，耗时、token、完整答案和原始日志见 [边界测试记录](week06_test_log.md)。测试完成后 Ollama 已恢复；密钥未入库。
