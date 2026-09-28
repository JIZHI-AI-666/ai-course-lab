# Week 3：Python 词汇练习生成器

本目录是可单独下载、运行和提交的 W3 作业包；不依赖仓库外的文件。

## 文件说明

| 文件/目录 | 用途 |
| --- | --- |
| `vocab_tool.py` | 主程序：读取词表并生成练习 |
| `data/生词表.csv` | 本次练习使用的词汇数据 |
| `练习.txt` | 已生成的 HSK4 按词性分组造句练习 |
| `实验记录.md` | 实验过程与 4 条本周新知识点 |
| `week03_Python_作业提交.zip` | 以上内容的独立提交压缩包 |

## 运行

需要 Python 3，无第三方依赖。

```bash
# 默认：按词性分组，覆盖生成本目录中的 练习.txt
python vocab_tool.py

# 可选：填空题模式
python vocab_tool.py --mode fill

# 可选：筛选其他等级
python vocab_tool.py --level 5
```

脚本通过自身文件位置定位 `data/`，因此可从任何目录运行。
