# 作业 4 · 加分项：smolagents 与手写工具循环对照（路径 A）

本机 16GB 内存，满足讲义路径 A 配置；`pip install smolagents`（**1.26.0**，与讲义核实的最新版一致）后，把当堂的 `hsk_level` 换成 `@tool` 形式，用本机 Ollama `qwen2.5:1.5b`（OpenAI 兼容端点）真实跑通了 `ToolCallingAgent` 最小示例。

## 一、运行记录（真实运行，证据见 evidence）

`smolagents_demo.py` 的 `@tool` 版 `hsk_level`（类型注解 + `Args:` docstring，即「约束即文档」），经 `OpenAIModel(model_id="qwen2.5:1.5b", api_base="http://localhost:11434/v1")` 驱动：

- **问句**：'把'字是 HSK 几级词汇？
- **框架行为**：Step 1 模型以原生 tool calling 点名 `hsk_level`，参数 `{"word": "把"}`；Step 2 调 `final_answer(answer='把 是 3 级')` 收口，共 2 步、0.48 秒、输入 2223 tokens / 输出 47 tokens
- **最终回答**：把 是 3 级——与手写循环当堂轨迹的查询结果一致（生词表里「把」确实是 3 级）
- **原始证据**：[smolagents_run_20261116.json](evidence/smolagents_run_20261116.json)（框架日志含逐步 tool call；本机为脚本运行，未截屏，框架完整输出已存档）
- **一处适配说明**：本机未配置云端密钥，`api_key` 传本地占位 `"local"`；真实密钥仍只放 `.env`，绝不写进代码——红线同样适用于加分项

## 二、五步映射表（全员最低要求）

源码位置为本机实装版本（smolagents 1.26.0，`site-packages/smolagents/`）实际核对过的位置：

| 我写的 tool_agent.py | smolagents 里对应什么 |
|---|---|
| `TOOLS` 字典：名字 → 函数 | `@tool` 装饰器（`tools.py:1061`）经 `get_json_schema` 把带类型注解与 `Args:` 文档的函数变成 `SimpleTool` 子类（`name`/`description`/`inputs`/`output_type` 四个类属性），交给 `ToolCallingAgent(tools=[...])` |
| `SYS` 提示词要求输出 JSON | `ToolCallingAgent`（`agents.py:1215`）不走手写提示词，`_step_stream` 里把 `tools_to_call_from=self.tools_and_managed_agents` 传给 `model.generate`，用模型原生 tool calling；系统提示模板在 `prompts/toolcalling_agent.yaml` |
| `parse_calls` 剥围栏、兜底抓 JSON | 框架内部解析 `ChatMessage.tool_calls`（`ChatMessageToolCall`），不用自己写正则；`stop_sequences=["Observation:", "Calling tools:"]` 防串台 |
| 按名字从 `TOOLS` 取函数执行，带异常兜底 | 框架按 `Tool.inputs`（即 JSON schema）先校验参数再调用，结果作为 Observation 写进 `ActionStep` 进入多步消息 |
| `run()` 手动回喂 + `max_calls` 收口 | `MultiStepAgent`（`agents.py:268`）管理多步循环与 `max_steps` 停止条件；我传了 `max_steps=5`，框架自动在模型调 `final_answer` 工具时结束 |

## 三、300 字反思：手写循环 vs 框架各管了什么

先手写再看框架，才看得出框架替我省了什么、又拿走了什么。省掉的是三层脏活：参数校验（JSON schema 自动生成并前置校验）、输出解析（不用再猜模型会不会老实输出一行 JSON）、循环管理（`max_steps`、日志、收口全是现成的）。本机 1.5B 模型在手写循环里需要 `FEED_TEMPLATE` 约束才肯正常收口，框架里同一模型两步就干净结束——说明「收口难」主要难在提示词工程，框架把这块工程量吃掉了。拿走的则是控制权：工具怎么向模型描述、失败信息怎么回喂、循环几步停，全藏进了抽象层，我不再能像改 `FEED_TEMPLATE` 那样一句话改行为；本周会诊出的「复读不收口」「拒绝信息被歪曲」两类问题，在框架里就只能读它的源码找开关。所以两者不是替代关系：手写 60 行教会我循环里有哪四道防线，框架教我这些防线在工业界长什么样。另按讲义要求注明出处与许可证：本项目为 Hugging Face 官方 smolagents（Apache-2.0，包内 LICENSE 已核对），允许使用与署名，但引用不等于可以不写出处。最后是安全呼应：框架里的 CodeAgent 会让模型生成 Python 代码并直接执行，能力更强、风险更大，必须放在受控环境——与本周「绝不用裸 eval」是同一条红线的两个端点。

## 四、材料与出处

- 安装：`pip install smolagents`（PyPI：https://pypi.org/project/smolagents/ ）
- 官方文档：https://huggingface.co/docs/smolagents/index
- HF Agents Course（课程清单 W9–12 阶段项）：https://huggingface.co/learn/agents-course
- 源码仓库：https://github.com/huggingface/smolagents
- 许可证：Apache-2.0（https://www.apache.org/licenses/LICENSE-2.0 ，包内 LICENSE 已核对）
