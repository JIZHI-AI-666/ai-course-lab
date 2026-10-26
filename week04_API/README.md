# 第四周 第一次 API 调用

验收入口：[机器人](week4_api_bot.py)、[三题完整日志](chat_log.txt)、[参数体验记录](参数体验记录.md)、[密钥安全自查表](密钥安全自查表.md)、[作业实录](作业实录.md)、[失败实验](失败实验.md)。

本周 chat_log.txt 是从本机恢复的 2026-10-12 原始日志，包含首次截断、三题回答、四组参数实验和缩短提示词后的重试。模型回答原样保留，不能当成权威教学结论。

```bash
python -m pip install -r requirements.txt
# 复制根目录 .env.example 为 .env，仅在本机填密钥
python week04_API/week4_api_bot.py --batch
python week04_API/week4_api_bot.py --experiment
python -m unittest discover -s week04_API -p 'test_*.py' -v
```

新运行默认追加到本周 local_logs/chat_log.txt（Git 忽略），防止公开日志误混真实学生材料。提交前只将审核过的通用问答整理入本周 chat_log.txt；留档日志不被自动改写。新参数报告为 参数体验记录_新运行.md，不覆盖已有观察。

费用可通过 --input-price 与 --output-price 传入官网当天每百万 token 单价；旧日志不能反推出历史账单。模拟失败实验不产生真实 API 用量。
