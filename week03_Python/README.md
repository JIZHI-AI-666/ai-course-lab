# 第三周 Python 与 AI 结对编程

必交材料：[脚本](vocab_tool.py)、[AI辅助编程实录](AI辅助编程实录.md)、[生成的练习](练习.txt)。另有 [语法复习卡片](语法复习卡片.md) 与 [验证记录](验证记录.md)。

按周归档：输入为本周 [data/生词表.csv](data/生词表.csv)，默认输出为本周练习.txt；根目录 weekpath.py 负责统一解析路径。从任意工作目录运行脚本，默认输出位置不变。原 ZIP 放在 [archive/](archive/)，过程原件放在 [evidence/](evidence/)。请下载整个仓库运行。

```bash
python week03_Python/vocab_tool.py
python week03_Python/vocab_tool.py --mode fill --output week03_Python/填空练习.txt
python week03_Python/vocab_tool.py --level 5 --output week03_Python/五级练习.txt
python -m unittest discover -s week03_Python -p 'test_*.py' -v
```

四步：load_words 读表，filter_by_level 挑等级，count_by_pos 统计词性，gen_grouped_exercises 写题。填空模式只对已有完整例句的词挖空，其他词明确退回造句题。

词表等级是课程练习标签，不据此宣称已核验官方词汇等级。
