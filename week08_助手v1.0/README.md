# 学科智能问答助手 v1.0

把第 2 周提示词、第 6 周双引擎 `llm.py`、第 7 周知识库 `rag_qa.py` 用一个粘合层串起来。不重写积木，只接线。

## 功能

- 基于 RAG 的学科问答：`use_rag=True` 先检索《等级标准》节选再答，`False` 走纯对话，同一套代码两种模式。
- `prefer="local"` / `"api"` 把第 6 周本地优先、云端兜底原样透传，首选失败自动回退并打印原因。
- 默认三问覆盖语法点、数字指标、课堂活动，任一题失败不会让整场演示退出。
- 知识库来源可追溯：每个检索片段带标题、章节与编号，答案中的 `[S编号]` 可回查原文。

## 怎么装

- 需要 Python 3.10+（本机验证为 3.13.12），并已启动 Ollama。
- 在仓库根目录执行：`python3 -m pip install -r week08_助手v1.0/requirements.txt`
- `ollama pull qwen2.5:0.5b`；嵌入模型优先 `ollama pull nomic-embed-text`。本机若因代理改用了 `nomic-embed-text:w7-f16`，助手会自动识别，也可 `export EMBED_MODEL=nomic-embed-text:w7-f16`。
- 复制仓库根目录 `.env.example` 为 `.env`，只在本机填写 `DEEPSEEK_API_KEY`；不要提交 `.env`。纯本地演示可以不配密钥。

## 怎么用

- 在仓库根目录运行：`python week08_助手v1.0/assistant_v1.py`
- 纯对话：`python week08_助手v1.0/assistant_v1.py --no-rag`
- 云端引擎：`python week08_助手v1.0/assistant_v1.py --prefer api`
- 单题：`python week08_助手v1.0/assistant_v1.py --prefer local "根据GF 0025—2021，四级累计词汇量是多少？"`
- 留原始数据：`python week08_助手v1.0/assistant_v1.py --json "四级累计词汇量是多少？"`

## 已知问题

- 未启动 Ollama 时本地检索和本地生成都会失败；可先打开 Ollama，或设 `prefer="api"` 只解决生成、不能代替本地嵌入。
- 知识库目前是 GF 0025—2021 节选，不含把字句教学难点和《愚公移山》活动设计；这两问开 RAG 时，合格表现是「资料中未提及」，不要把流畅编造当成成功。
- 0.5B 本地模型即使检索到四级累计词汇 3245，仍可能答错或漏标出处；数字以语料和官方标准为准。
- 未配置 `DEEPSEEK_API_KEY` 时 `prefer="api"` 会打印切换原因并回退本地，不会写入密钥。
- 本机实测没有云端密钥，因此**云端引擎没有真实作答的证据**，只有回退到本地的证据；换到配好密钥的机器才能补上云端实测。

## 文件

| 文件 | 作用 |
|---|---|
| `assistant_v1.py` | 粘合层：`answer(question, use_rag=True, prefer="local")` 与三问三答主程序 |
| `run_demo.py` | 采集演示记录，原始输出存 JSON，不改写模型回答 |
| `answer_log.md` | 演示记录：7 条，四要素齐全，含失败与不一致的诚实结论 |
| `evidence/demo_run_20261109.json` | 本次演示的原始回答、引擎、耗时、检索依据 |
| `requirements.txt` | 本周依赖清单 |
| `../week08/rag_mapping.md` | 官方 RAG 流水线 5 行映射表（全员最低要求） |
| `../week08/read_notes.md` | 官方文档与 llm-universe C3/C4 的读数笔记 |
| `../week08/reflect.md` | 300 字反思：与官方 2-Step 的差距、Agentic 需要补什么、许可证与 .env 红线的共同点 |
| `../week08/peer_review.md` | 第 8 周互评记录（评阅李悦同学作品集，四维度） |
| `../week06_双引擎/llm.py` | W6 双引擎：写答案 |
| `../week07_RAG/rag_qa.py` | W7 知识库：找资料 |

## 依赖关系

```text
assistant_v1.py（本周粘合层）
├── llm.py        ← week06_双引擎/    负责生成
└── rag_qa.py     ← week07_RAG/        负责检索
    └── weekpath.py ← 仓库根目录/       跨周 import 与 .env 加载
```

三块积木各自独立可跑，本周只做接线与规范化，没有复制第三套模型调用代码。
