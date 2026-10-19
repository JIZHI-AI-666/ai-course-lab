# 第五周本地部署作业

主笔记：[ollama_notes.md](ollama_notes.md)。包含安装、选型、五问本地与云端对比、官方文档学习、不同量级比较与离线部署方案。

原始证据：`questions.json` 保存统一题目和预设检查点；`results/*.json` 保存真实回答、耗时、token 和本地模型运行占用。云端题目仅含通用知识和虚构文本。

## 复现

Python 3.9+，仅用标准库，先安装 Ollama 并准备模型。在本目录运行：

```bash
python3 run_comparison.py --backend local --model qwen2.5:0.5b
python3 run_comparison.py --backend local --model qwen2.5:1.5b
python3 run_comparison.py --backend cloud --model deepseek-chat --env-file /你的本地路径/.env
```

`.env` 使用上周的 `DEEPSEEK_API_KEY`，可选 `DEEPSEEK_BASE_URL`。密钥仅本地保存，不进入命令参数或仓库。云端运行会调用 API 并产生相应用量。结果文件已存在时脚本拒绝覆盖；先将旧结果归档再重跑。网络错误时已成功的逐题结果保留，不能把部分结果当作完整实验。

## 提交边界

指定阅读《轻量级开源模型的离线部署》的原文尚未取得，笔记中已明确标出。离线方案已写，但不声称完成指定文章阅读或整机断网演练。官方文档三条用法已整理，学生仍需阅读理解并亲自演示。
