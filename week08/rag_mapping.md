# 官方 RAG 流水线 ↔ 我的 rag_qa.py / assistant_v1.py（5 行映射表）

- 制作时间：2026-11-11
- 对照对象：LangChain 官方 RAG / Retrieval 文档（<https://docs.langchain.com/oss/python/langchain/rag>、<https://docs.langchain.com/oss/python/deepagents/retrieval>）；Datawhale llm-universe（<https://github.com/datawhalechina/llm-universe>）第一部分 C3「搭建向量知识库」、C4「构建 RAG 应用」
- 我的代码：[week07_RAG/rag_qa.py](../week07_RAG/rag_qa.py)、[week08_助手v1.0/assistant_v1.py](../week08_助手v1.0/assistant_v1.py)

第三列全部对着自己的源码写，函数名与类名逐个从文件里核过。

| 行 | 官方流水线（必须覆盖） | llm-universe 对应章节 | 我自己的代码 |
|---|---|---|---|
| 1 | **Load + Split** | C3「3.3 数据处理」→ 3.3.2 数据读取、3.3.4 文档分割 | `rag_qa.py` 的 `load_chunks(corpus=CORPUS)`：`TextLoader(str(corpus), encoding='utf-8').load()[0].page_content` 读入 → 按 `re.split(r'(?m)(?=^## )', text)` 先切章节 → `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=['\n\n','\n','。','；',' ',' '], add_start_index=True)` 切块。类名：`TextLoader`、`RecursiveCharacterTextSplitter`。常量：`CHUNK_SIZE, CHUNK_OVERLAP = 500, 50`；语料文件名：`data/等级标准节选.txt`（`CORPUS = WEEK_DIR / 'data' / '等级标准节选.txt'`） |
| 2 | **Embed + Store** | C3「3.1 向量及向量知识库」「3.2 使用 Embedding API」「搭建并使用向量数据库」 | `rag_qa.py` 的 `get_store(rebuild=False, *, corpus=CORPUS, persist=PERSIST)`：`OllamaEmbeddings(model=EMBED_MODEL, base_url=os.getenv('LOCAL_BASE_URL','http://127.0.0.1:11434'), client_kwargs={'trust_env': False})` 生成向量 → `Chroma(collection_name='w7_' + signature[:24], persist_directory=str(persist), embedding_function=emb, client_settings=Settings(anonymized_telemetry=False))` **本地持久化**到 `week07_RAG/chroma_db/`。嵌入模型名：常量 `EMBED_MODEL = os.getenv('EMBED_MODEL', 'nomic-embed-text')`（本机实际为 `nomic-embed-text:w7-f16`）；数据不出本机。集合名用 `corpus_signature()` 的 `sha256` 摘要区分，语料或嵌入配置一变即换集合，不混用旧索引 |
| 3 | **Retrieve** | C4「4.2 构建检索问答链」→ 4.2.1 加载向量数据库、4.2.2 创建检索链 | `rag_qa.py` 的 `get_retriever(k=3, rebuild=False)` → `get_store(...).as_retriever(search_kwargs={'k': 3})`，top-k = 3；对外入口 `retrieve_documents(question, k=3)` 与 `retrieve(question, k=3)`。查询前用 `retrieval_query()` 去掉固定的版本前缀。**`use_rag=True` 时的调用顺序**：`assistant_v1.py` 的 `answer()` → `retrieve(question)` 取片段 → `build_prompt(question, ctx)` → `llm.ask(...)`；`use_rag=False` 时**完全跳过 retrieve**，直接进 `llm.ask()` |
| 4 | **Prompt + Generate** | C4「4.1 将 LLM 接入 LangChain」「4.2.4 构建检索问答链」 | `rag_qa.py` 的 `build_prompt(question, ctx)` 拼四段：「只根据以下参考资料回答，不用记忆补充」+「资料中没有的内容就如实说'资料中未提及'」+「用中文简答，不超过150字。数值区分新增和累计，每个事实后标注对应[S编号]」+ `<资料>…</资料> 问题：…`；再由 `assistant_v1.py` 在前面接 `SYSTEM_HINT = "你是国际中文教学助手，面向 HSK3–4 学习者，回答需给出依据。"`。最后调用的函数是 **`llm.ask(prompt, prefer=prefer)`**，其中 `llm = LLM()`（W6 `week06_双引擎/llm.py`），`prefer` 取 `"local"` 或 `"api"`，由 `answer(question, use_rag=True, prefer="local")` 透传 |
| 5 | **Deploy + Evaluate** | C4「4.3 部署知识库助手」（Streamlit）；C5「5.1 如何评估 LLM 应用」「5.2 评估并优化生成部分」 | 部署：本周是命令行入口 `assistant_v1.py`（`main()` 跑 `QUESTIONS` 三问），**W15 再用 Streamlit 发布**。评估：W7 幻觉对照表 [week07_RAG/hallucination_log.md](../week07_RAG/hallucination_log.md)（同题裸答 vs RAG 答逐条留痕）；W8 另有 [answer_log.md](../week08_助手v1.0/answer_log.md) 7 条记录，含 `use_rag` 开/关对照与 `prefer=api` 回退证据，原始数据在 `evidence/demo_run_20261109.json` |

## 三个可迁移点（读数结论）

### 1. 组件可替换

官方原句：

> Each component is modular: you can swap loaders, splitters, embeddings, or vector stores without rewriting the app's logic.

我实际换掉了两处，**应用逻辑一行没改**：

- **embeddings**：官方示例用云端 embedding，llm-universe 用 OpenAI/文心/讯飞/智谱四家 API，我换成本地 `OllamaEmbeddings(model='nomic-embed-text')`——只改了 `get_store()` 里的一行，检索与生成代码完全没动。
- **语料**：官方索引英文文档站，llm-universe 索引自己的 PDF/文档，我换成《国际中文教育中文水平等级标准 GF 0025—2021》课程整理节选——只改了 `CORPUS` 常量。

反过来，**换语料后最容易出的事我踩过并处理了**：索引残留会让新旧资料混答。所以 `corpus_signature()` 把「语料内容 + 嵌入模型 + 分块配置 + 章节切分版本」一起做 sha256，摘要变了就换集合名；`get_store(rebuild=True)` 还会先 `delete_collection()` 再重建，避免把半途失败的索引当成完整的。

### 2. 统一模型入口

llm-universe 把 GPT / 文心一言 / 讯飞星火 / 智谱 GLM 的 API 统一封装成一个调用接口（对应 C4 的 4.1.1–4.1.4 四小节）。我对照的是 W6 的 `LLM().ask(prompt, prefer="local" | "api")`：调用方只传 `prompt` 和 `prefer`，不必每次改地址和返回字段，本地优先、云端兜底、双向 try/except 回退。

**接口形状几乎一致**：官方用 `init_chat_model(model=..., tools=[...])`，llm-universe 用 `ChatOpenAI(temperature=0, openai_api_key=...)`；我的 `LLM.ask()` 把这些差异藏在 `LocalEngine` / `APIEngine` 两个类后面，`assistant_v1.py` 不知道背后是谁。这正是「上层不需要知道背后是谁」这一点的具体落点。

### 3. 评估闭环

C5「系统评估与优化」把评估拆成生成部分与检索部分分别评估。我的对应物是 W7 幻觉对照表——同一道题裸答与 RAG 答并排列出，逐条写差距与原因。这是「不轻信输出，用可核对的资料验证」的做法。

**我对照中发现的一个真实缺口**：C4 有 4.2.5「向检索链添加聊天记录」和 4.2.6「带有信息压缩的检索链」两节，我的 v1.0 都没有。这意味着：

- 多轮追问会丢上下文（第二轮起 `retrieve()` 拿不到上一轮的指代对象）；
- 检索片段多时提示词会变长，但我的 `build_prompt()` 固定 k=3 且限 150 字，某种程度上靠「少检索」绕过了「压缩」问题——是规避不是解决。

## 官方三类架构与我的位置

| 架构 | 官方定义 | 我的对应 |
|---|---|---|
| **2-Step RAG** | 检索总在生成之前，简单可预测，LLM 调用次数有上限 | **v1.0 就是这一类**：`use_rag=True` 时先 `retrieve()` 再 `ask()`，`False` 时直接 `ask()` |
| Agentic RAG | 由 LLM 在推理中自行决定何时、如何检索 | 本周不做。按官方说法，它「only thing an agent needs is access to one or more tools that can fetch external knowledge」——正是 W9 的工具调用 |
| Hybrid RAG | 中间加入查询改写、检索校验、答案校验 | 本周不做。W15 做评估时可回看；我的 `answer_details()` 已经能返回 `sources` 与 `invalid_citations`，是答案校验的雏形 |

**`use_rag` 这个布尔开关的设计依据就在这里**：官方把 2-Step 的定义写成「检索 always happens before generation」，也就是说 2-Step 里「不检索」不是一个独立架构，而是**关闭检索后剩下的纯对话**。我的开关正是把这两件事放进同一份代码，关闭时检索环节根本不发生——所以 LLM 调用次数与提示词长度都可控，行为可预测、可复现。
