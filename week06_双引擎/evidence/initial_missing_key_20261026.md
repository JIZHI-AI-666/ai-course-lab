# 第六周边界测试记录

测试时间：2026-10-26。机器：Apple M4，16 GiB，Ollama 0.40.6，本地模型 `qwen2.5:0.5b`。统一学科问题：给《愚公移山》出一道 HSK4 阅读理解题（题干须依据课文情节）。

增强项：`llm.py` 打印耗时；云端另打 token 与示意费用。本次本机未找到可用的 `DEEPSEEK_API_KEY`（仓库按要求不保存 `.env`），云端成功作答这一格留空，回退日志仍按原文记录。

## 测试表（≥5 组）

| # | 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期／怎么改的 |
|---|---|---|---|---|
| 1 | Ollama 开，`prefer="local"` | 本地 `qwen2.5:0.5b` | 冷加载约 4.00s，`eval_count=415`，`done_reason=stop`。题干把愚公移山说成出自《三国演义》，选项与解析整体跑题。速度快，不能当阅读题用。 | 符合「本地直连」。质量差是 W5 已观察到的 0.5B 问题，不是封装失败。隐私向任务仍应走本地，再由教师改题。 |
| 2 | 关掉 Ollama 后 `prefer="local"` | 本地失败，代码已切换云端；云端因未配置密钥未能作答 | 回退日志见下方原文。程序没有把异常 `pass` 掉，也没有返回空字符串。 | 回退逻辑符合预期。不符合「切到云端后给出答案」这一格，原因是本机没有 `.env`。处理：根目录复制 `.env.example` 为 `.env` 填入密钥后重跑 `run_boundary_tests.py 2 --stop-ollama`。 |
| 3 | `prefer="api"`，密钥未配置（云端不可用） | 云端失败 → 自动切本地 | 见组 4 原文。本地约 3.70s，`eval_count=468`。答案把愚公移山改写成联合国在里约热内卢做移山工程，并出现曾国藩，属于严重幻觉。 | 符合「云端挂了回本地、程序不崩」。也证明：断网/没密钥时课堂演示可以继续，但 0.5B 内容必须人工拦。 |
| 4 | 同组 3，作为「云端不可用 + prefer=api」专项 | 云端 → 本地 | 切换原因打印完整，见原文。 | 符合课后作业补测要求。 |
| 5 | Ollama 开，`prefer="local"`，`max_tokens=15` | 本地 | 热调用 0.28s，`eval_count=15`，`done_reason=length`。输出停在「设计一道 H」，明显截断。 | 符合预期：`num_predict`/`max_tokens` 是上限不是目标长度。出题任务不要把上限设这么小。 |

## 组 2 回退日志原文（最关键证据）

```
条件: Ollama 关，prefer=local（期望打印回退日志后走云端）
Ollama 当前: 关
[首选引擎失败，自动切换] HTTPConnectionPool(host='127.0.0.1', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=11434): Failed to establish a new connection: [Errno 61] Connection refused"))
[本地失败，自动切换云端] HTTPConnectionPool(host='127.0.0.1', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=11434): Failed to establish a new connection: [Errno 61] Connection refused"))
RuntimeError: 未配置 DEEPSEEK_API_KEY（纯本地模式请 prefer='local'）
```

测完脚本已执行 `open -a Ollama`，11434 恢复可访问。

## 组 4 回退日志原文

```
条件: 临时清空 DEEPSEEK_API_KEY，prefer=api（期望回退本地）
[首选引擎失败，自动切换] 未配置 DEEPSEEK_API_KEY（纯本地模式请 prefer='local'）
[云端失败，自动切换本地] 未配置 DEEPSEEK_API_KEY（纯本地模式请 prefer='local'）
[耗时与费用] engine=local  3.70s  本地免费  eval_count=468  done_reason=stop
```

## 组 1 / 组 5 调用日志原文

```
[耗时与费用] engine=local  4.00s  本地免费  eval_count=415  done_reason=stop
[耗时与费用] engine=local  0.28s  本地免费  eval_count=15  done_reason=length
```

## 反思：什么任务固定走本地，什么固定走云端

`prefer` 不是开关装饰，是 W5 选型笔记的代码化。

固定走本地的：真实学生作文、成绩、评语、班级名单、任何能指向未成年人的文本。数据不出本机是红线，比答案漂亮更优先。格式固定、可人工核对的批量练习（抄写、选词填空）也可以本地，因为高频调用不按 token 计费，错了教师改得过来。教室断网或演示「程序不能崩」时，默认 `prefer="local"`，失败才会去云端。

固定走云端的：复杂教案、多步推理、需要正确情节和干扰项的阅读题。今天同一道愚公移山出题，0.5B 两次都编造课文没有的事实（三国演义、里约热内卢、曾国藩）。这种题不能交给本地小模型定稿。云端也不是权威：涉及 HSK4 词汇量、语法点数量，必须回查《等级标准》，不能把模型数字写进讲义。

拿不准时用 `prefer="local"`：本地挂了有回退；云端挂了也能回本地。缺的不是接口，是密钥和人工核验。配好 `.env` 后应补跑组 2、组 3，把云端耗时、token 和示意费用填进本表。

