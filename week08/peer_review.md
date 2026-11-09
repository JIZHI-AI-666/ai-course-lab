# 第 8 周互评记录：评阅李悦（f25052211）的作品集

- **评阅人**：刘静（f25210111）
- **评阅对象**：李悦（f25052211）
- **对象仓库**：https://gitee.com/hayleybeiii/ai-portfolio
- **评阅时间**：2026-11-09
- **复现环境**：macOS（Apple Silicon）/ Python 3.13.12 / Ollama 已启动，本地模型 `qwen2.5:0.5b`，本地嵌入 `nomic-embed-text:w7-f16`，未配置 `DEEPSEEK_API_KEY`
- **依据**：《第8周指定互评分配表》第 f25210111 行；四维度按讲义第七节与分配表第三节
- **纪律**：本表只记录我照着做时看到的现象，不打分、不评价人。别人的仓库我只是读取与运行，未做任何修改。

---

## 复现步骤（我实际执行的命令）

```bash
git clone https://gitee.com/hayleybeiii/ai-portfolio.git
cd ai-portfolio
python3 -m venv .venv && source .venv/bin/activate
# 见「维度 2」：README 写的安装命令在仓库根目录会失败，需进子目录
cd week08_助手v1.0 && pip install -r requirements.txt
cd week08_助手v1.0 && python assistant_v1.py
cd week08_助手v1.0 && python assistant_v1.py --no-rag
cd week08_助手v1.0 && PREFER=api python assistant_v1.py
```

克隆后仓库自带 `v1.0` 标签，`git log` 可见 10 次提交，最近一次为「W8: 新增 3 分钟路演脚本（含可能追问与答法）」。

---

## 维度 1 · 能不能跑

**现象：能跑通。`python assistant_v1.py` 无报错退出，三问都有回答。**

第一次运行时程序自动在仓库根目录生成了 `chroma_db/`（我先确认过 `git ls-files chroma_db` 返回 0 个文件，`.gitignore` 第 22 行有 `chroma_db/`，索引没有入库）。

三问的实际输出摘要：

| 问题 | 是否回答 | 输出摘要 | 我的运行时长 |
|---|---|---|---|
| 把字句的教学难点有哪些 | 有 | 列出词汇量、语法结构、句式练习、语境运用、语言运用灵活性 5 条 | 约 1.1s |
| HSK4 词汇量要求是多少 | 有 | 答「HSK4 拥有 2245 个汉字」，并引用了语料里「等次 4 级别 音节 900 个，汉字 199/468 个，词汇 2245 个，语法点 210 个」这一行 | 约 0.2s |
| 《愚公移山》可以设计什么课堂活动 | 有 | 列出角色扮演、小组讨论、情景剧表演、故事剧、口头作文 5 类活动 | 约 1.5s |

`--no-rag` 也跑通，三问都有回答。本回答是纯对话模式的输出：把字句答「语感培养、语法学习、语境理解……」10 条；HSK4 答「2,000 以上」。

**云端路径的报错原文**（本机没有密钥，属预期）：

```text
[api 第 1/3 次失败] 未配置 DEEPSEEK_API_KEY（云端引擎不可用）
[api 第 2/3 次失败] 未配置 DEEPSEEK_API_KEY（云端引擎不可用）
[api 第 3/3 次失败] 未配置 DEEPSEEK_API_KEY（云端引擎不可用）
[首选引擎 api 失败，自动切换 local] 引擎 api 重试 3 次仍失败：未配置 DEEPSEEK_API_KEY（云端引擎不可用）
```

云端不可用时自动切换本地并继续作答，没有中断。

**一个我没找到说明的现象**：脚本只跑内置的三问，命令行传问题不生效。我执行 `python assistant_v1.py "四级累计词汇量是多少"`，程序仍然输出三问（把字句 / HSK4 / 愚公移山），传进去的字符串没有被使用。README 的「怎么用」里也没有提到这一点。

---

## 维度 2 · README 能复现吗

**现象：能跑通，但安装那一步的路径需要先明确，否则会卡住。**

README「怎么装」写的是：

```text
- `pip install -r requirements.txt`
```

我在**仓库根目录**执行这一句，报错原文：

```text
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

原因是我先 `find` 过了：整个仓库只有一个 `requirements.txt`，路径是 `week08_助手v1.0/requirements.txt`，根目录没有。README 的「怎么用」明确写了「在 `week08_助手v1.0` 目录下运行」，所以我改为先 `cd week08_助手v1.0` 再执行 `pip install -r requirements.txt`，这次成功，依赖装齐。

**所以复现路径是：安装和运行都要在 `week08_助手v1.0` 目录内，README 的安装句没有像运行句一样标出这个目录。** 如果照着「怎么装」在根目录做，第一步就会失败。

其余步骤与 README 描述一致：

- `ollama pull qwen2.5:0.5b && ollama pull nomic-embed-text` —— 我本机已有，未重新拉取。
- 密钥「放进系统环境变量 `DEEPSEEK_API_KEY`（不要写进仓库里的任何文件）」—— 我检查了克隆下来的仓库，`.env` 不存在，根目录有 `.env.example`；`.gitignore` 第 1 行起覆盖 `.env`。
- 「首次运行会自动建库到仓库根目录 `chroma_db/`」—— 实测符合：我删掉 `chroma_db/` 后再运行，程序自动重新生成。
- 「换语料后加 `REBUILD=1` 重建」—— 实测 `REBUILD=1 python assistant_v1.py` 能正常跑完，无报错。

**一个环境相关的现象**：本机嵌入模型的标签是 `nomic-embed-text:w7-f16`（此前因代理问题未用默认标签），我需要 `export EMBED_MODEL=nomic-embed-text:w7-f16` 才能建库。README 与代码默认值都是 `nomic-embed-text`，没有提到 `EMBED_MODEL` 这个环境变量。如果别人机器上装的是默认标签，这一步不需要额外设置，属于环境差异，不算缺陷。

---

## 维度 3 · Release 发了吗

**现象：发了，标签与页面说明都能查到。**

- 远端标签：`git ls-remote --tags` 返回 `refs/tags/v1.0` 与 `refs/tags/v1.0^{}`，指向 commit `29ce826`。
- Gitee Release 页面：https://gitee.com/hayleybeiii/ai-portfolio/releases/tag/v1.0 ，标题「学科智能问答助手 v1.0」，`prerelease: false`，创建时间 `2026-11-09T13:02:43+08:00`，`target_commitish` 为 `29ce826ae3fbf6d29e65954826570e8356b2c733`。

**说明齐全**，我用 Gitee API 读了 Release 正文全文，四个部分都在：

| 部分 | Release 正文里的内容 |
|---|---|
| 功能 | `use_rag` 开关、双引擎本地优先云端兜底、资料没有就说「资料中未提及」不硬编 |
| 安装 | `pip install -r week08_助手v1.0/requirements.txt`、`ollama pull qwen2.5:0.5b && ollama pull nomic-embed-text`、密钥放系统环境变量 |
| 用法 | `cd week08_助手v1.0`、`python assistant_v1.py`、`--no-rag`、`PREFER=api` |
| 已知问题 | 知识库只覆盖《等级标准》节选、本地 0.5b 质量有限、首次运行需下载嵌入模型约 140MB |

Release 里给出的安装命令带了 `week08_助手v1.0/` 前缀，路径是完整的——这一点和 README 根目录那句 `pip install -r requirements.txt` 写法不一致，两个页面各写了一种。

---

## 维度 4 · 有没有已知限制

**现象：写了。README 有独立的「已知问题」段，Release 里也有对应段落。**

README「已知问题」逐条写的是：

1. 未启动 Ollama 时本地引擎会报错，可设 `PREFER=api` 走云端；两者都不可用时脚本会打印「运行失败：原因」而不是崩掉。
2. 知识库目前只覆盖《等级标准》节选，问把字句教学法、课文活动设计这类问题会得到「资料中未提及」——这是设计如此，不是 bug。
3. 本地 `qwen2.5:0.5b` 质量有限（例如会把四级词汇说成 300），演示建议用 `PREFER=api`。
4. 首次运行需下载嵌入模型（`nomic-embed-text`，约 140MB），离线环境需提前准备好。

**我照着这些限制逐条对照，有一条与我的实测不一致，如实记下**：

第 2 条说问「把字句教学法」会得到「资料中未提及」。我在语料里 grep 过，`data/等级标准节选.txt` 全文 0 处「把字句」，检索确实没命中相关内容；但我用本地 `qwen2.5:0.5b` 跑这一问，输出的是一段关于「字词积累、语法结构、句式练习、语境运用、语言运用灵活性」的具体教学建议，**没有出现「资料中未提及」**。同一问在 `--no-rag` 下也是类似的内容。

仓库自带的 `week08_助手v1.0/answer_log.md` 里，第 1 组与第 3 组的 use_rag=True 答案记录写的是「资料中未提及」，标注引擎为 `prefer=api（deepseek-chat）`。我在本机没有 `DEEPSEEK_API_KEY`，云端路径没能真实跑起来，所以这两次的差异我无法判定是引擎不同造成的，还是同一模型两次输出不同——我只能记下看到的现象。

第 3 条「会把四级词汇说成 300」我这边没复现：RAG 模式答的是 2245（并引用了语料原文那一行），纯对话模式答「2,000 以上」。数字都不等于语料里的「1000/3245」。

第 1 条和第 4 条与实测相符：云端与本地都不可用时确实打印「[运行失败] 原因」而不是崩掉（我看到的原文是 `[api 第 1/3 次失败] 未配置 DEEPSEEK_API_KEY（云端引擎不可用）` 与 `[首选引擎 api 失败，自动切换 local]`，随后仍给出了答案）；嵌入模型确实需要预先下载。

---

## 我看到的其他材料（供参考，不计入四维度）

这些不属于分配表规定的四个维度，但确实是仓库里存在的材料，记录一下以便核对：

- `week08/映射表.md`：官方 RAG 五步流水线（Load+Split / Embed+Store / Retrieve / Prompt+Generate / Deploy+Evaluate）逐行对照到自己的 `rag_qa.py` / `assistant_v1.py`，另附三个可迁移点与许可证说明。
- `week08/reflect.md`：A 路径 300 字反思。
- `week08/作业2_已知问题为什么诚实写.md`：200 字说明。
- `week08/W9工具清单.md`：W9 预习的两个工具。
- `week08/演示脚本.md`：3 分钟路演脚本，含可能追问与答法。
- `week08_助手v1.0/answer_log.md`：三问三答的演示记录，每条四要素齐全，另附「use_rag 该按答案能否在资料里找到来开关」的小结。
- 语料 `data/等级标准节选.txt` 用表格形式列出各等次音节/汉字/词汇/语法点的新增与累计数值，我核对过：四级词汇为 `1000/3245`，与 GF 0025—2021 一致。

---

## 复现时写下的步骤清单

如果我要把这条路径再走一遍，会按这个顺序：

1. `cd ai-portfolio/week08_助手v1.0`（**先进入子目录**，这是安装与运行的前提）
2. `pip install -r requirements.txt`
3. 本地嵌入标签与默认不同时：`export EMBED_MODEL=<你的标签>`
4. `python assistant_v1.py` → 三问
5. `python assistant_v1.py --no-rag` → 纯对话对照
6. `PREFER=api python assistant_v1.py` → 有密钥时走云端；无密钥时观察回退日志
7. 需要重建索引时加 `REBUILD=1`
