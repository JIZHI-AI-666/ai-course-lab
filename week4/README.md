# Week 4 第一次 API 调用作业

本目录在课程 `week04_API` 骨架上完成，覆盖讲义中的达标、良好和优秀评分点：单题调用、3 个学科问题、参数实验、token 与费用记录、日志追加、缺密钥与网络错误提示。

## 1 安装与配置

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

然后只在本机编辑 `.env`，把占位值替换成自己的 DeepSeek API 密钥。真实密钥不得写进代码、截图、聊天记录或仓库。

## 2 完成三项作业操作

```bash
# 单题调用
python week04_API/week4_api_bot.py "把字句的教学难点有哪些"

# 自动运行 3 个国际中文教育专业问题
python week04_API/week4_api_bot.py --batch

# 自动完成 temperature 与 max_tokens 的 4 组对比
python week04_API/week4_api_bot.py --experiment
```

运行后：

- `chat_log.txt` 保存真实问答、参数、耗时与 token 用量；按原代码包规则，该文件已被 `.gitignore` 排除。
- `week4_实验记录.md` 保存可提交的参数对比表，可加入仓库作为作业证据。
- 如需费用估算，请从所用平台当天价格页取得每百万 token 单价，再运行：

```bash
python week04_API/week4_api_bot.py --batch --input-price 输入单价 --output-price 输出单价
```

代码不会硬编码可能变化的价格，也不会猜测费用。

## 3 本地测试

测试不访问网络，也不需要密钥：

```bash
python -m unittest week04_API/test_week4_api_bot.py -v
```

## 4 提交前检查

- [ ] 已实际运行 `--batch`，`chat_log.txt` 中有 3 次专业问答。
- [ ] 已实际运行 `--experiment`，`week4_实验记录.md` 不再显示“待运行”。
- [ ] 已阅读并评价模型回答，具体数字已用教材或权威标准核验。
- [ ] `.env` 只在本机，代码中没有 `sk-...` 真实密钥。
- [ ] `git status` 中没有 `.env`。
- [ ] 若密钥曾泄露，已在平台后台吊销并重新生成。
