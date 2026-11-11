# 第 8 周开源对照 · 读数笔记（read_notes.md）

阅读时间：2026-11-11。材料：LangChain 官方 Retrieval 文档（docs.langchain.com → Retrieval / 2-Step RAG 段）与 Datawhale llm-universe 第一部分 C3、C4。仅用浏览器阅读，未安装任何依赖。

## 一、2-Step RAG 是什么

官方把索引拆成四步——Load（把数据源读成 `Document` 对象）、Split（用 splitter 把大文档切成小块）、Embed（把每块转成向量）、Store（用 VectorStore 存下分块与向量）；检索与生成则是运行时的另外两步。**2-Step RAG 指检索永远在生成之前执行**：「In 2-Step RAG, the retrieval step is always executed before the generation step.」官方表格里它的特点是「Simple and predictable」「Latency: Fast」，并特别说明「the maximum number of LLM calls is known and capped」——LLM 调用次数有上限、延迟可预期，适合 FAQ 与文档机器人。对照 Agentic RAG：由 LLM 在推理中自己决定何时、如何检索，延迟不固定，需要工具调用能力。

官方关于组件的一句话原文：

> Each component is modular: you can swap loaders, splitters, embeddings, or vector stores without rewriting the app's logic.

## 二、C3 做了什么

C3 标题是「搭建向量知识库」，实际包含四件事：**3.1 向量及向量知识库**（词向量与向量、向量数据库）、**3.2 使用 Embedding API**（OpenAI、文心千帆、讯飞星火、智谱四家云端嵌入）、**3.3 数据处理**（源文档选取、数据读取、数据清洗、文档分割）、**3.4 搭建并使用向量数据库**。前三件是准备工作，第四件是把前三件的产物落成可检索的库。它额外附了一篇《LangChain自定义Embedding封装讲解》。

## 三、C4 做了什么

C4 标题是「构建 RAG 应用」，三件事：**4.1 将 LLM 接入 LangChain**（分别用 LangChain 调用 ChatGPT、百度文心一言、讯飞星火、智谱 GLM）、**4.2 构建检索问答链**（加载向量数据库 → 创建检索链 → 创建 LLM → 构建检索问答链 → 向检索链添加聊天记录 → 带有信息压缩的检索链）、**4.3 部署知识库助手**（Streamlit 简介 → 构建应用程序 → 部署应用程序）。另附《LangChain自定义 LLM》。

它比 C3 多出的两个环节很关键：**4.2.5 聊天记录**让问答链有多轮上下文，**4.2.6 信息压缩**处理检索内容过长的问题——这两项我的 v1.0 都没有。

## 四、两个资源的关系（读数结论）

C3/C4 与官方文档不是并列的两套做法，而是**同一套流水线在两个抽象层上的写法**：C4 的 4.2「加载向量数据库 → 创建检索链 → 创建 LLM → 构建检索问答链」就是官方 Retrieval pipeline 的具体落地。官方是组件契约（Document、splitter、embedding、VectorStore 各自可换），C3/C4 是工程实现（用哪家云端 API、怎么切块、怎么用 Streamlit 上线）。

**一个具体的差异**：llm-universe 的嵌入走云端 API（OpenAI/文心/讯飞/智谱），官方示例用 `InMemoryVectorStore`，而我的实现用本地 `nomic-embed-text` + 本地持久化 Chroma。三者都符合「嵌入可替换」这一条——这正是讲义说的「改得动才算真懂」。

## 五、许可证事实核对

按讲义要求实际查了 llm-universe 仓库根目录：`LICENSE`、`LICENSE.txt`、`LICENSE.md`、`license` 四种命名全部返回 404，**仓库确实没有 LICENSE 文件**，按默认规则「保留所有权利」：可以读、可以学思路、可以在反思里署名引用，不可把它的代码复制进自己的仓库。

根目录实际内容：`docs/`、`notebook/`、`data_base/`、`figures/`、`requirements.txt`、`README.md`、`.env`、`.gitignore`——与讲义描述的目录结构一致。
