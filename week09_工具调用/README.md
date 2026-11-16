# W9 · 手写最小工具调用循环（tool_agent.py）

从「会答」到「会做」：W8 的助手只能生成文字，本周让模型自己决定「下一步调哪个工具」。不依赖任何框架，手写约 150 行把 Function Calling 的四步接力串起来：**模型输出 JSON（决定）→ `parse_calls` 解析 → 程序执行工具 → 结果回喂 → 模型据此作答**；`max_calls=2` 到顶强制收口。

## 功能

- 三个工具，`TOOLS` 字典统一注册，模型只能点名、执行权在代码：
  - `get_time`：查当前系统时间，让模型「知道现在」；
  - `calc`：白名单 AST 四则运算，**绝不裸 eval**——只放行数字与 `+ - * / ** %`，越权表达式返回「拒绝计算」；
  - `hsk_level`：查生词表 CSV 返回 HSK 等级，确定数据靠查表不靠模型记。
- `parse_calls` 三重容错：剥 ` ```json ` 围栏、跨行抓 JSON 块、多行并列调用逐块提取（1.5B 小模型实测常一口气点名两个工具）。
- 一轮内执行模型点名的全部工具并合并回喂；工具异常转成文字继续，不让单次失败打断循环。
- 引擎口径与讲义一致：默认云端 `deepseek-chat`，设 `DEEPSEEK_BASE_URL`/`DEEPSEEK_MODEL` 即切本机 Ollama（OpenAI 兼容端点）；本地端点自动放开代理对 localhost 的拦截。

## 怎么装

- Python 3.10+（本机验证 3.13.12），本机演示需已启动 Ollama 并 `ollama pull qwen2.5:1.5b`。
- 在仓库根目录执行：`python3 -m pip install -r week09_工具调用/requirements.txt`
- 云端口径：复制根目录 `.env.example` 为 `.env`，填入 `DEEPSEEK_API_KEY`；**不要提交 `.env`**。
- 本机口径（无需密钥）：`export DEEPSEEK_BASE_URL=http://localhost:11434/v1 DEEPSEEK_MODEL=qwen2.5:1.5b`

## 怎么用

```bash
# 复合问句（讲义指定题，模型分别点名 hsk_level 与 get_time）
python week09_工具调用/tool_agent.py
# 自带问题
python week09_工具调用/tool_agent.py 帮我算一下 35*24 等于多少
# 采集全部调用轨迹（原始输出存 evidence/，不改写模型回答）
python week09_工具调用/run_traces.py --output week09_工具调用/evidence/trace_run_20261116.json
```

## 交付与证据

| 文件 | 作用 |
|---|---|
| `tool_agent.py` | 手写最小工具调用循环：三个工具 + `parse_calls` 容错解析 + `run()` 循环 |
| `run_traces.py` | 轨迹采集脚本：4 组真实调用（含 1 组口语式会诊素材），原始输出存 JSON |
| `call_log.md` | **3 条调用轨迹记录**（四要素齐全）＋ 1 条会诊素材 ＋ 稳定性观察 ＋ 验收单逐项对照 |
| `evidence/trace_run_20261116.json` | 原始模型输出、解析结果、工具返回、最终回答，未手工改写 |
| `requirements.txt` | 本周依赖（openai、python-dotenv） |

## 已知问题

- 本机未配置云端密钥，**云端 deepseek-chat 口径没有本机实测证据**；实测模型为 Ollama `qwen2.5:1.5b`，与讲义教师机 8B 规模相近（讲义五连跑全对，本机 1.5B 方差明显，见 `call_log.md` 第三节）。
- 1.5B 模型收到「拒绝计算」后可能复读被拒调用，靠 `max_calls` 收口兜底；最终回答可能是未经组织的 JSON 原文（轨迹 3 实录）。
- 口语式复合问句会答一半（轨迹 4 实录），与讲义第六节预测一致；问句措辞本身是约束手段。

## 与前后周的接线

- 复用 W3 的 `week03_Python/data/生词表.csv`（经根目录 `weekpath.py` 定位），复用 W8「工具给事实、模型给解释」的原则。
- W8 `W9工具清单.md` 里许愿的「查生词表」「算分」正是本周的 `hsk_level` 与 `calc`——预习清单被课堂直接兑现。
- 进阶方向（课后作业 2）：把 W7 的 `retrieve()` 包成第 4 个工具，体会「从 2-Step 走向让模型自己决定何时检索」；W10 将把「工具不在本机」的问题交给 MCP 协议。
