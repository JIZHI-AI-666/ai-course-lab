# 第 8 周互评记录：评阅陈佳怡（L25000016）的作品集

- **评阅人**：刘静（f25210111）
- **评阅对象**：陈佳怡（L25000016）
- **对象仓库**：https://github.com/chintanavolavong/L25000016
- **评阅时间**：2026-11-11
- **复现环境**：macOS（Apple Silicon）/ Python 3.13.12 / Ollama 已启动，本地模型 `qwen2.5:0.5b`，本地嵌入 `nomic-embed-text:w7-f16`，未配置 `DEEPSEEK_API_KEY`
- **依据**：《第8周指定互评分配表（更新版）》第 f25210111 行（该表按平台分组修订，本次 GitHub 组错开 10 位）；四维度按分配表第三节
- **纪律**：本表只记录我照着做时看到的现象，不打分、不评价人。我只读取与运行对方的仓库，未做任何修改。

---

## 复现步骤（我实际执行的命令）

```bash
git clone https://github.com/chintanavolavong/L25000016.git
cd L25000016
python3 hello.py                 # 能跑
python3 assistant_v1.py          # 文件不存在
python3 rag_qa.py "HSK4 词汇量要求是多少"
python3 week06_双引擎/test_week6.py
python3 vocab_tool.py
python3 week4_api_bot.py
```

克隆后仓库共 11 次提交，最近一次为 `11aec9b Add files via upload`（2026-11-05），该次提交新增了 `rag_qa.py` 与 `第七周RAG实验报告.docx` 两个文件。

---

## 维度 1 · 能不能跑

**现象：`assistant_v1.py` 不存在，三问无从跑起。我改跑仓库里实际存在的入口，得到以下结果。**

### `assistant_v1.py`

仓库全库（`find` 排除 `.git`）没有 `assistant_v1.py`，根目录与任何子目录下都没有。执行结果：

```text
python3: can't open file '/private/tmp/peer2/target/assistant_v1.py': [Errno 2] No such file or directory
```

因此讲义与分配表要求的「`python assistant_v1.py` 有无报错、三问是否都有回答」这一项，在当前仓库状态下无法执行——没有可运行的助手入口。

### 根目录 `weekpath.py` 缺失，连带影响 W3/W4/W6/W7

`rag_qa.py`、`week06_双引擎/llm.py`、`vocab_tool.py`、`week4_api_bot.py` 都在开头 `import weekpath`，但仓库根目录没有 `weekpath.py`（`find` 全文搜索无此文件）。因此这几个入口全部报同一个错：

```text
ModuleNotFoundError: No module named 'weekpath'
```

我逐个实测的原文：

| 入口 | 结果 |
|---|---|
| `python3 rag_qa.py "HSK4 词汇量要求是多少"` | `ModuleNotFoundError: No module named 'weekpath'` |
| `python3 week06_双引擎/test_week6.py` | `ModuleNotFoundError: No module named 'weekpath'`（`from llm import LLM` 导入 llm.py 时触发） |
| `python3 vocab_tool.py` | `ModuleNotFoundError: No module named 'weekpath'` |
| `python3 week4_api_bot.py` | `ModuleNotFoundError: No module named 'weekpath'` |
| `python3 hello.py` | ✅ 正常输出：`Hello, AI! 我的第一个程序跑通了。` |

我另外单独验证了 `week06_双引擎/llm.py` 本身能否被导入，结果同样是 `ModuleNotFoundError: No module named 'weekpath'`——它的第 7 行 `import weekpath` 是硬依赖。

### 语料文件也不在仓库里

`rag_qa.py` 第 29 行 `CORPUS = weekpath.data_path("等级标准节选.txt")`，但仓库里没有 `data/` 目录，全库搜索也没有任何名为「等级标准节选」的文件（`find` 结果里只有 `练习.txt`、`chat_log.txt`、`week06_双引擎/fallback_test_results.txt`、`week06_双引擎/test_results.txt` 四个 txt）。

即使补上 `weekpath.py`，`rag_qa.py` 仍会在 `TextLoader(CORPUS)` 处因语料缺失而失败。

**小结**：当前仓库状态下，能跑通的只有 W1 的 `hello.py`；本周的助手入口 `assistant_v1.py` 不存在；W3/W4/W6/W7 的入口因缺 `weekpath.py` 与语料而全部无法启动。

---

## 维度 2 · README 能复现吗

**现象：README 只有一行标题，没有「怎么装」和「怎么用」，无法照着复现。**

README.md 全文（11 字节）：

```markdown
# L25000016
```

我用 `grep` 逐个关键词检查，结果：

| 关键词 | 是否存在 |
|---|---|
| 功能 | ✗ |
| 怎么装 | ✗ |
| 怎么用 | ✗ |
| 已知问题 | ✗ |
| assistant_v1 | ✗ |
| v1.0 | ✗ |

**没有安装步骤，也没有运行命令**，所以「照着 README 的『怎么装 / 怎么用』一步步做」这一步无从开始——不是卡在某一步，是文档里没有可执行的动作。

不过从代码本身能看出作者写过的运行说明，只是没有写进 README。我把从代码里读到的信息记在这里，供对照：

- `rag_qa.py` 文件头注释写了依赖与准备：
  ```text
  # 依赖：pip install langchain langchain-community langchain-chroma langchain-ollama chromadb
  # 准备：ollama pull nomic-embed-text
  ```
- `rag_qa.py` 末尾注释写了用法：`python rag_qa.py "问题"`，默认问题为「HSK4 要求掌握哪些语法点？」，并注明 `prefer="local"` 用于隐私任务。
- `week06_双引擎/` 下有 `test_week6.py`、`test_fallback_mock.py` 两个测试脚本与 `test_results.txt`、`fallback_test_results.txt` 两份结果文件。

**我实际卡住的地方**：我按代码注释装好依赖后，运行 `rag_qa.py` 仍停在 `import weekpath` 这一步——需要仓库根目录有 `weekpath.py`。这一文件在仓库中不存在，无法从仓库内获得。

---

## 维度 3 · Release 发了吗

**现象：远端没有 v1.0 标签，也没有 Release 页面。**

- **标签**：`git ls-remote --tags origin` 返回空，没有任何标签。
- **Release**：调用 `https://api.github.com/repos/chintanavolavong/L25000016/releases` 返回空数组 `[]`，该仓库没有创建过任何 Release。
- **week08 目录**：访问 `https://github.com/chintanavolavong/L25000016/tree/main/week08` 返回 HTTP 404，仓库没有 week08 目录。
- **仓库可见性**：`private: False`，是公开仓库，别人可以直接打开，不存在「私有未加观察者」的情况。

因此「远端有无 v1.0 标签、Release 页面的功能 / 安装 / 用法是否齐全」这一维度没有可检查的对象——标签与 Release 都没有创建。

仓库基本信息：默认分支 `main`，最近推送 `2026-11-04T16:22:01Z`（仓库页面显示的提交时间为 11-05，两者对应同一次上传）。

---

## 维度 4 · 有没有已知限制

**现象：README 里没有「已知问题」这一段，也没有以任何形式写出限制。**

README 全文只有 `# L25000016` 一行（见维度 2），`grep` 检查「已知问题」关键词无结果。仓库里没有单独的已知问题说明文件。

代码里能找到的提示性注释（我读到的原文）：

- `rag_qa.py` 的 `build_prompt()` 里写了拒答要求：`资料中没有的内容就如实说"资料中未提及"`；
- `rag_qa.py` 的 `get_retriever()` 注释说明了延迟构建与索引复用：`延迟构建：import 本模块不会触发 embedding 计算，只有真正检索时才建库；已存在 chroma_db 则直接复用`；
- `rag_qa.py` 注释标注了隐私取向：`隐私任务用 prefer="local"；复杂任务用 prefer="api"`。

这些是代码内的说明，**不等于 README 里的「已知问题」**。我没有在仓库任何位置找到类似「未启动 Ollama 会报错」「知识库只覆盖某范围」「0.5B 模型质量有限」「首次运行需下载嵌入模型」这类使用限制的成段说明。

---

## 我看到的其他材料（供参考，不计入四维度）

这些不属于分配表规定的四个维度，但确实是仓库里存在的材料，记录一下以便核对：

- `week06_双引擎/`：`llm.py`、`test_week6.py`、`test_fallback_mock.py`、`reflection.md`、`test_results.txt`、`fallback_test_results.txt`。`llm.py` 是 W6 双引擎封装，与讲义要求的结构一致。
- `rag_qa.py`：W7 知识库问答器。写法上有两处值得记录——`get_retriever()` 用模块级 `_retriever` 变量做延迟构建，import 时不触发 embedding 计算；`Chroma` 持久化到 `weekpath.root_path("chroma_db")` 且已有索引时直接复用，不重复建库。`build_prompt()` 带了「资料中没有就说未提及」的拒答措辞。
- `第七周RAG实验报告.docx`（29KB，11-05 提交）：W7 的实验报告。
- `prompt-library/`：6 个提示词文件（作文批改、修改记录、生词筛选、语法练习、课堂活动、出题.md、教案扩展.md）。
- `AI辅助编程实录.md`、`ollama_notes.md`、`chat_log.txt`、`vocab_tool.py`、`week4_api_bot.py`、`练习.txt`：W1–W5 的交付物。
- 5 张 `屏幕截图 2026-10-*.png`：W5 本地部署期间的截图。
- `week06_双引擎/__pycache__/llm.cpython-313.pyc`：**编译缓存被提交进了仓库**。这不是本周要求的内容，但它是唯一一个我看到「本不该入库却入库了」的文件。

---

## 复现时写下的步骤清单

如果我要把这条路径再走一遍，会按这个顺序：

1. `git clone https://github.com/chintanavolavong/L25000016.git`
2. `cd L25000016 && python3 hello.py` —— 确认基础环境能跑通
3. `python3 rag_qa.py "HSK4 词汇量要求是多少"` —— 当前会停在 `import weekpath`
4. 查清缺什么：仓库根目录需要 `weekpath.py`，`data/` 目录需要 `等级标准节选.txt`
5. 本周主线入口 `python3 assistant_v1.py` —— 当前文件不存在
6. 远端标签与 Release：`git ls-remote --tags origin`、Releases API —— 当前均为空
