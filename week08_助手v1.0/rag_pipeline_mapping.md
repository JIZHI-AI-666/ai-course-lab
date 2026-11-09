# 官方 RAG 流水线 5 行映射表

讲义第六节第 3 点的「全员最低要求」：一张 5 行流水线映射表。左侧是官方标准流水线，右侧是我自己写的 `rag_qa.py` / `assistant_v1.py`。

对照对象（讲义指定的两个资源，均在课程清单内）：

- 主线：LangChain 官方 RAG 教程 <https://docs.langchain.com/oss/python/langchain/rag>；RAG 架构与 2-Step RAG 专页 <https://docs.langchain.com/oss/python/deepagents/retrieval>
- 中文对照：Datawhale llm-universe <https://github.com/datawhalechina/llm-universe>，在线阅读 <https://datawhalechina.github.io/llm-universe/>

## 五步流水线映射

| 官方流水线 | llm-universe 对应章节 | 我的 rag_qa.py / assistant_v1.py |
|---|---|---|
| **Load + Split** 加载与分块 | C3 数据处理：读取、清洗与切片 | `TextLoader` 读取 `week07_RAG/data/等级标准节选.txt` → `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`，按 `##` 章节先切再分块，每块带 `section` / `chunk_id` 元数据 |
| **Embed + Store** 向量化入库 | C3 词向量及向量知识库、搭建并使用向量数据库 | `OllamaEmbeddings(model="nomic-embed-text")` 生成向量 → `langchain_chroma.Chroma` 本地持久化到 `week07_RAG/chroma_db/`；用 `sha256(语料+嵌入配置)` 作为集合名，资料或配置变更即换集合，不混用旧索引 |
| **Retrieve** 检索 | C4 基于 LangChain 搭建检索问答链 | `rag_qa.py` 的 `retrieve(question, k=3)` → `as_retriever(search_kwargs={"k":3})` 取 top-3；`assistant_v1.py` 里 `use_rag=True` 才走这一步，`False` 直接跳过 |
| **Prompt + Generate** 拼词与生成 | C4 将 LLM 接入 LangChain | `build_prompt(question, ctx)` 拼「只根据资料回答 + 资料中没有就说未提及 + 标注 [S编号]」→ 交给 W6 的 `LLM().ask(prompt, prefer=...)` 生成；`SYSTEM_HINT` 是 W2 提示词库落地的一句人设 |
| **Deploy + Evaluate** 部署与评估 | C4 Streamlit 部署知识库助手；C5 系统评估与优化 | 评估用 W7 六组幻觉对照表（本地裸答/云端裸答/本地RAG/云端RAG 四路留痕）+ W8 的 `answer_log.md` 七条演示记录；部署留到 W15 用 Streamlit，本周只做命令行入口 |

## 三个可迁移点的实际落点

| 可迁移点 | 官方 / 中文教程里的做法 | 我代码里的对应 |
|---|---|---|
| 组件可替换 | 官方明确 loaders / splitters / embeddings / vector stores 都能单独替换，不必改应用逻辑 | 把云端 embeddings 换成本地 `nomic-embed-text`、英文语料换成 HSK 等级标准节选，就是我的 v1.0；换语料只需换 `CORPUS` 常量 |
| 统一模型入口 | llm-universe 把 GPT / 文心 / 讯飞 / 智谱 GLM 的 API 统一封装成一个调用接口，一键切换模型 | W6 的 `LLM().ask(prefer="local" \| "api")` 本地优先、云端兜底，是同一个思路：`assistant_v1.py` 的 `prefer` 参数只透传，不自己写 HTTP |
| 评估闭环 | llm-universe C5 分别评估并优化生成部分与检索部分 | W7 幻觉对照表是最朴素的评估证据：同一问题裸答 vs RAG 答逐条留痕；W8 补充了 `use_rag` 开/关的同题对照（`answer_log.md` 记录 1 与 4、2 与 5） |

## 官方 2-Step RAG 与本项目的对应

官方文档把 RAG 分成 2-Step RAG、Agentic RAG、Hybrid 三类。2-Step 指「检索总在生成之前」，简单可预测、LLM 调用次数有上限。

我的 v1.0 正是 2-Step：`use_rag=True` 时先 `retrieve()` 再 `ask()`，`False` 时直接 `ask()`。这与 `use_rag` 布尔开关的设计完全对应——**开关关闭时，检索环节根本不发生**，因此 LLM 调用次数与提示词长度都可控。

Agentic RAG（让模型自己决定何时检索）不在本周范围，按讲义留到 W9 工具调用。这也是我把 `use_rag` 做成显式布尔值而不是自动判断的原因：2-Step 阶段的行为需要可预测、可复现。

## 分层路径说明

本次按 **C 路径**（浏览器读文档 + 本机已有积木跑通）完成：

| 路径 | 任务范围 | 本次是否完成 |
|---|---|---|
| A | 跑通官方 2-Step 最小示例 → 映射表 → 换 HSK 资料改造 → 300 字反思 | 未做（需跑官方示例） |
| B | 只读官方文档与 llm-universe C3/C4 源码，用云端 API 完成映射表 + 1 个改造点 | 未做（本机无云端密钥） |
| C | 浏览器读文档，交 5 行映射表 + 300 字反思 | **已完成**（映射表 + 反思见下） |

分层不影响本周 Release 与互评的考核标准。本机跑通了 W6/W7 的本地积木，所以映射表的每一行都对着实际跑通的代码核对过，不是照抄文档。

## 改造点（1 个）

**把 `build_prompt` 的拒答指令从「提示」变成「硬约束」，并在答案生成后做一次自检。**

官方与 llm-universe 的最小示例通常默认「模型会照资料答」，但本次实测发现 0.5B 本地模型会无视「资料中没有的内容就如实说'资料中未提及'」这句提示，把「结构清晰、语法准确、语境理解」这类通用套话包装成依据（见 `answer_log.md` 记录 1）。

我的改造方向是让拒答不依赖模型自觉：

1. `build_prompt` 保留原有拒答措辞，但把「不要记忆补充」写成第一句；
2. 生成后检查答案里是否出现 `[S编号]` 标记——一个都没出现，说明模型没引用任何检索到的片段，视为可疑答案；
3. 此时在输出里追加提示「本次回答未引用任何检索片段，请人工核对」，把判断权交回使用者。

本机 `answer_details()` 已经把 `sources` 和 `answer` 分开返回，为第 2、3 步留好了接口。这条改造尚未完全实现，列为 v1.1 待办——**这里如实标注状态，不把计划写成已完成**。

## 300 字反思

对照下来最有价值的不是「我少写了哪些代码」，而是看清了**组件边界在哪里**。官方流水线把加载、切块、向量化、入库、检索、拼词、生成拆成七个可替换组件，看上去零件更多；但真拆开看，我的 `rag_qa.py` 与它的差别主要在两处：入库时我多了一个「语料+配置签名」的集合隔离机制，避免资料更新后新旧索引混答；生成时我多了一个「资料没有就说未提及」的拒答约束。前者解决真实踩过的坑，后者解决真实遇到的失败——**这两点都不是教程里抄来的，是自己跑出来的**。

另一个体会是「组装 ≠ 重写」这句话的实感。v1.0 里真正新写的代码只有一个 `answer()` 函数和一段 `try/except`，剩下的检索、生成、路由全部复用前七周的积木。如果当时把 `llm.py` 复制一份改改，助手能跑，但第六周的边界测试记录就再也无法验证这个项目了——**能替换的模块，才谈得上能测试**。

最后是评估。官方把评估拆成生成与检索两部分，llm-universe C5 讲得更细。回头看自己第六、七周的对照表，其实已经无意识地做了同样的事：W7 把裸答和 RAG 答分开留痕，才发现 RAG 会答错数值。**如果只跑通一遍不看对照，我大概会以为「加了 RAG 就更准了」**——事实是它只是让错误变得可查。这大概就是 C5 所说的「评估闭环」的意思：不看评估，就不知道自己在优化什么。

## 许可证与引用声明

- LangChain 官方文档：按其要求注明出处即可，本表引用了两条官方链接。
- llm-universe 仓库未附 LICENSE 文件，按默认规则保留所有权利：**仅阅读、学思路、署名引用，未复制其代码入库**。本表中的「llm-universe 对应章节」列仅为章节名对照。
- 语料为《国际中文教育中文水平等级标准 GF 0025—2021》课程整理节选，来源见 `week07_RAG/data/README.md`。
- 本项目代码为本人课程作业，使用 AI 辅助编写（方案与验证由本人完成）。
