# 第五周 本地部署

[主笔记](ollama_notes.md)包含安装排错、按内存选型、五个相同问题的本地与云端比较、术语、隐私和课后思考。实验数据记录日期为2026-10-19。

- [统一题目与评价点](questions.json)
- [原始回答和指标](results)
- [复现脚本](run_comparison.py)
- [Model配置](Modelfile)

```bash
# 在本目录运行；先安装Ollama并准备对应模型
python run_comparison.py --backend local --model qwen2.5:0.5b
python run_comparison.py --backend local --model qwen2.5:1.5b
python run_comparison.py --backend cloud --model deepseek-chat --env-file /你的本机路径/.env
```

现有结果不会被覆盖，重跑前请先另行归档。云端调用产生实际用量，只有本机保存密钥。结果中每题一次测试，不推广为所有模型的总体排名。

模型量级比较、Modelfile和乡村学校方案属于扩展。课堂演示和个人术语理解需本人完成；方案不等于已经进行整机断网演练。
