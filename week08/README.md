# 第 8 周：开源对照与课后作业

本目录是第八周课后交付的入口。当堂交付的 v1.0 主线（`assistant_v1.py` + 四段式 README + requirements + tag v1.0 + Release）在 [../week08_助手v1.0/](../week08_助手v1.0/README.md)。

## 文件

| 文件 | 对应任务 | 说明 |
|---|---|---|
| [read_notes.md](read_notes.md) | 开源拆解 · 第 1 步（全员） | 读数笔记：2-Step RAG 是什么、C3 做了什么、C4 做了什么，附许可证事实核对 |
| [rag_mapping.md](rag_mapping.md) | 开源拆解 · 第 2 步（全员最低要求） | 官方 RAG 流水线 5 行映射表，第三列全部对着自己的源码写 |
| [reflect.md](reflect.md) | 开源拆解 · 第 3、4 步（全员） | 300 字反思，答完三问；含 C 路径要求的改造方案（写明具体组件名） |
| [peer_review.md](peer_review.md) | 课后作业 3 | 互评记录：评阅陈佳怡（L25000016），四维度只描述现象 |
| [作业2_已知问题为什么诚实写.md](作业2_已知问题为什么诚实写.md) | 课后作业 2 | 200 字说明 |
| [W9工具清单.md](W9工具清单.md) | 课后作业 3 | W9 预习：希望助手拥有的两个工具及其输入输出 |

## 引用与来源声明

RAG 流水线设计参考 LangChain 官方 Retrieval 文档（<https://docs.langchain.com/oss/python/langchain/rag>、<https://docs.langchain.com/oss/python/deepagents/retrieval>）；知识库助手结构参考 Datawhale llm-universe C3/C4（<https://github.com/datawhalechina/llm-universe>，在线阅读 <https://datawhalechina.github.io/llm-universe/>）——**仅参考思路，未复制代码**。

llm-universe 仓库未附 LICENSE 文件，按默认规则保留所有权利：可阅读、学思路、署名引用，不可复制其代码入库。本目录中的每一行映射表第三列均从自己的 `week07_RAG/rag_qa.py` 与 `week08_助手v1.0/assistant_v1.py` 源码逐个核对得出。

语料为《国际中文教育中文水平等级标准 GF 0025—2021》课程整理节选，来源与核对说明见 [../week07_RAG/data/README.md](../week07_RAG/data/README.md)。

`.env` 与密钥不入仓；本目录不含任何真实密钥。
