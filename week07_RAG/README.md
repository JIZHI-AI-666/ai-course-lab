# 第七周：RAG 学科知识库问答器

本周产出：加载文本 → 分块 → 本地嵌入 → Chroma 检索 → 复用第六周 `LLM.ask()` 生成答案。进阶选择“来源引用”，每个片段记录标题、章节、编号及来源，答案和原始检索依据一同保留。

| 验收项目 | 文件 |
|---|---|
| 可运行程序、可导入的 rag_qa 接口 | [rag_qa.py](rag_qa.py) |
| 公开学科语料、来源及版本说明 | [语料](data/等级标准节选.txt)、[来源说明](data/README.md) |
| 六组裸答/RAG对照、约200字反思 | [hallucination_log.md](hallucination_log.md) |
| 完整原始回答、片段、参数、用量 | [实验JSON](evidence/experiment_20261102.json) |
| 同题四路复现实验 | [run_experiments.py](run_experiments.py) |
| 索引重建、来源、边界回归测试 | [test_rag_qa.py](test_rag_qa.py)、[验证记录](验证记录.md) |
| 第八周项目目录与待补功能 | [week08_plan.md](week08_plan.md) |
| 教师原始代码与语料 | [原始骨架](evidence/teacher_rag_qa.py.txt)、[原始语料](evidence/teacher_corpus.txt) |

## 现场演示（已配置的电脑）

双击本目录 **demo.command** → 如提示则输入密钥（不显示、不保存）→ 输入 **1、2、3** 选择演示问题。

启动器会定位仓库、选择已有虚拟环境、尝试启动本机Ollama并识别已安装的嵌入模型。默认真实调用云端，屏幕展示问题、答案、引用原文、实际引擎与耗时；不会展示大段JSON。也可以直接输入自定义问题，输入q退出。请投屏前完成密钥输入和一次彩排。

终端运行：`./week07_RAG/demo.command`。需要查看完整原始数据时，对下面的rag_qa.py命令添加 `--json`；排版不改写模型答案，也不保证模型每次回答一致。

## 安装与运行

从仓库根目录执行，Python 3.12 为本次验证环境。共享模块 `weekpath.py` 和第六周 `llm.py` 必须一起下载。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r week07_RAG/requirements.txt
# 先启动 Ollama
ollama pull nomic-embed-text
ollama pull qwen2.5:0.5b
# 需要云端时，复制根目录 .env.example 为 .env 并填写自己的密钥；不要覆盖已有配置
python week07_RAG/rag_qa.py '根据GF 0025—2021，四级累计词汇量是多少？' --retrieve-only
python week07_RAG/rag_qa.py '根据GF 0025—2021，四级累计词汇量是多少？' --prefer local
python week07_RAG/rag_qa.py '根据GF 0025—2021，四级累计词汇量是多少？' --prefer api
python week07_RAG/rag_qa.py --rebuild --retrieve-only
python -m unittest discover -s week07_RAG -p 'test_*.py' -v
```

实际环境的 `ollama pull` 遇到代理的非公网地址校验错误，改用模型作者提供的同系列 F16 文件导入。下载文件与数据库不提交 Git；模型标签如实记录为 `nomic-embed-text:w7-f16`。

[模型作者发布页](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/tree/0188c9bf409793f810680a5a431e7b899c46104c)。下载 `nomic-embed-text-v1.5.f16.gguf` 后，在该文件所在目录创建内容为 `FROM ./nomic-embed-text-v1.5.f16.gguf` 的 Modelfile，执行：

```bash
ollama create nomic-embed-text:w7-f16 -f Modelfile
export EMBED_MODEL=nomic-embed-text:w7-f16
```

实际模型文件 SHA256：`f7af6f66802f4df86eda10fe9bbcfc75c39562bed48ef6ace719a251cf1c2fdb`。若使用常规拉取的默认模型，保持 EMBED_MODEL 不设置即可，但不保证与本次结果完全相同。

复现实验会真实调用云端，使用自己的密钥；原始文件已存在时拒绝覆盖。请提供新文件名：

```bash
python week07_RAG/run_experiments.py --output week07_RAG/evidence/my_run.json
# 若中途失败，使用相同文件名加 --resume，仅补未完成项
```

## 索引、引用和边界

- 语料位于本周 `data/`，向量库位于本周 `chroma_db/`；路径相对脚本解析，不依赖终端当前目录，不改变第三周的数据路径。
- 按章节记录来源，再以500字符、50重叠切块。当前语料章节较短，每节各成一块；配置500/50不表示强行把短段填满。
- 用语料内容和嵌入配置的摘要区分集合，资料变更不会继续使用旧集合；`--rebuild` 清理当前集合后重新建库，避免重复追加。旧版本集合仍可留在本地数据库中，不参与当前检索。
- 查询只移除已固定的2021标准前缀，生成仍保留完整原问题；首轮漏检索与修正结果均在对照表中。
- `--k` 默认3；返回完整相关片段，不能把检索到top-k等同于“必然相关”。对照表逐题检查。
- `rag_qa(question, prefer="local")` 返回答案与完整检索依据；`rag_qa_details()` 返回原始答案、来源、耗时、实际引擎和引用编号检查。
- 检查引用编号是否存在不等于验证其语义。小模型可能看到了正确片段却答错，或标了编号但说法不受该片段支持；对照实验保留这些失败。
- 复用W6的双向回退：`prefer=local` 仍可能切云端。本次只用公开标准文本，不适合直接输入学生隐私信息。
- .env、密钥与 `chroma_db/` 均不入库。当前实验日期和新增提交时间如实记录。
