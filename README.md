# AI 课程作品集

《人工智能在学习环境中的应用与实践》；学科方向：国际中文教育。仓库：[JIZHI-AI-666/ai-course-lab](https://github.com/JIZHI-AI-666/ai-course-lab)。

## 每周交付索引

| 周次 | 主题 | 可直接读取的交付物 |
|---|---|---|
| W1 | 环境与 AI 学科任务 | [hello.py](hello.py)、[AI任务单](ai任务单.md)、[环境运行记录](week01_环境/环境验证记录.md) |
| W2 | 提示词工程 | [7个模板](prompt-library/README.md)、[提示词迭代实录](prompt-library/prompt_iteration_log.md) |
| W3 | Python 与 AI 结对编程 | [vocab_tool.py](week03_Python/vocab_tool.py)、[AI辅助编程实录](AI辅助编程实录.md)、[练习.txt](练习.txt)、[语法复习卡片](week03_Python/语法复习卡片.md) |
| W4 | 第一次 API 调用 | [week4_api_bot.py](week04_API/week4_api_bot.py)、[chat_log.txt](chat_log.txt)、[参数体验记录](week04_API/参数体验记录.md)、[密钥安全自查表](week04_API/密钥安全自查表.md) |
| W5 | 本地部署 | [ollama_notes.md](week05_本地部署/ollama_notes.md)、[统一题目](week05_本地部署/questions.json)、[原始回答与指标](week05_本地部署/results/) |
| W6 | 双引擎封装 | [代码与运行入口](week06_双引擎/README.md)、[五组边界测试](week06_双引擎/week06_test_log.md)、[RAG学科文本](week06_双引擎/学科文本_预习RAG.md) |

[逐项验收索引](作业验收索引.md) · [文件清单](submission_manifest.json) · [自查结果](验收结果.md)

所有必交正文均为普通文本文件，不需要解压 ZIP。旧 ZIP 和 week4/ 保留为历史快照；当前第四周入口是 week04_API/。根目录入口与对应周目录副本由完整性检查核对，避免抓取层级不同造成遗漏。

## 运行

需要 Python 3.10+。W1/W3 仅用标准库；W4 安装 requirements.txt。

```bash
python hello.py
python week03_Python/vocab_tool.py
python week03_Python/vocab_tool.py --mode fill --output week03_Python/填空练习.txt
python -m pip install -r requirements.txt
# 复制 .env.example 为 .env，在本机填入自己的密钥
python week04_API/week4_api_bot.py --batch
python week04_API/week4_api_bot.py --experiment
python tools/check_submission.py
```

W5 复现见 [本地部署说明](week05_本地部署/README.md)。日志与结果中的时间是其实际记录时间；本次整理不修改旧实验时间或旧 Git 提交。`chat_log.txt` 是审核后的课程公开日志，新运行写入被忽略的 local_logs/，不得直接提交真实学生材料或 .env。

## 验收边界

完整性程序检查文件、链接、同步副本和实验结构，不代替教师打分。本人逐行讲解、现场运行、雨课堂链接登记与截止时间由教师验收。第一、二周原始讲义未提供，相关材料按现有课程上下文整理；第三至六周按所提供讲义对应。
