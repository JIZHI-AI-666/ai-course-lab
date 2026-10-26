# AI辅助编程实录

## 1. 任务与提示词

任务：用Python标准库读取生词表CSV，筛选目标等级，统计词性，生成练习；课后扩展按词性分组与填空题。

历史来源：9月28日先向Codex提供教师代码骨架和作业截图，再提供仓库链接。可恢复的后续原始指令为：

> 你帮我把仓库里的文件按照周整理 week3的所有内容统一打包 方便老师抓取

首次需求以附件表达，未找到一段独立的“四件套”文字提示词，因此不追补一段文字并称它是9月原话。下面将任务整理成可复现的完整提示词，供当前复核：

```text
【角色】你是Python教学助手，帮助国际中文教育学生理解程序。
【任务】读取data/生词表.csv，按HSK等级筛选，统计词性，生成练习.txt。
【要求】只用标准库；UTF-8读写；函数分别完成读、筛、统、写；使用weekpath定位仓库根目录，不依赖工作目录；增加按词性分组与填空两种模式；填空题从完整例句替换目标词；没有例句时明确退回造句。给出完整代码与修改原因，不声称已经由学生独立手写。
【示例】用“坚持”造一个句子。（动词）；填空：学习汉语要每天____练习。
```

工具与分工：Codex生成和修改代码、执行验证；本记录依据实际文件和Git差异整理。本人需要在课堂复述关键代码并独立操作，工具通过测试不等同于已完成个人口头验收。未保存的手写稿不补造。

## 2. AI初版代码

下面完整代码来自9月28日本机保存的首次AI扩展版，基于教师骨架增加分组、填空和参数。不是从当前最终代码倒推虚构的初稿。原件：[20260928_ai_first.py.txt](week03_Python/evidence/20260928_ai_first.py.txt)；教师基线：[teacher_vocab.py.txt](week03_Python/evidence/teacher_vocab.py.txt)。

```python
# W3 生词表 CSV -> 自动生成练习题
# 运行：python vocab_tool.py
# 可选：python vocab_tool.py --mode fill（生成填空题）
import os
import csv
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  统一解析 data/ 路径，换目录也不会找不到文件

DATA = weekpath.data_path("生词表.csv")


def load_words(path=DATA):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def filter_by_level(words, level="4"):
    return [w for w in words if str(w["HSK等级"]) == str(level)]


def count_by_pos(words):
    d = {}
    for w in words:
        d[w["词性"]] = d.get(w["词性"], 0) + 1
    return d


def group_by_pos(words):
    """按词性把词条归类，便于分组复习。"""
    groups = {}
    for word in words:
        groups.setdefault(word["词性"], []).append(word)
    return groups


def gen_grouped_exercises(words, out=None):
    """生成按词性分组的造句练习。"""
    # 产物统一落到代码包根目录：否则"从哪个目录运行"决定了文件落在哪，
    # 与 README 的"任意目录运行"承诺冲突，且散落的产物 .gitignore 拦不住。
    out = out or weekpath.root_path("练习.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("HSK 词汇分组造句练习\n")
        f.write("=" * 24 + "\n\n")
        for pos, group in group_by_pos(words).items():
            f.write("【%s】\n" % pos)
            for w in group:
                f.write("- 用“%s”造一个句子。（释义：%s）\n" % (w["词汇"], w["释义"]))
            f.write("\n")


SENTENCE_TEMPLATES = {
    "把字句": "老师正在讲解____的用法。",
    "商量": "这件事我们明天再一起____吧。",
    "感动": "电影中的故事让我十分____。",
    "坚持": "学习汉语要每天____练习。",
}


def gen_fill_blank_exercises(words, out=None):
    """用目标词替换句子中的对应位置，生成填空题。"""
    out = out or weekpath.root_path("练习.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("HSK 词汇填空练习\n")
        f.write("=" * 24 + "\n\n")
        for index, w in enumerate(words, start=1):
            sentence = SENTENCE_TEMPLATES.get(
                w["词汇"], "请用“____”完成一个与“%s”有关的句子。" % w["词汇"]
            )
            f.write("%d. %s（提示：%s）\n" % (index, sentence, w["释义"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从生词表生成 HSK 词汇练习")
    parser.add_argument("--mode", choices=("group", "fill"), default="group",
                        help="group：按词性分组造句（默认）；fill：生成填空题")
    parser.add_argument("--level", default="4", help="要生成的 HSK 等级，默认 4")
    args = parser.parse_args()

    words = load_words()
    selected_words = filter_by_level(words, args.level)
    print("总词汇 %d 个，其中 HSK%s 词汇 %d 个，词性分布：%s"
          % (len(words), args.level, len(selected_words), count_by_pos(selected_words)))
    out = weekpath.root_path("练习.txt")
    if args.mode == "fill":
        gen_fill_blank_exercises(selected_words, out)
    else:
        gen_grouped_exercises(selected_words, out)
    print("已生成：%s" % out)

```

## 3. 修改点与原因

| 编号 | 从什么改成什么 | 原因与验证 |
|---|---|---|
|1|教师单行造句扩展为group_by_pos后按词性分组|按名词、动词组织复习；样例仍保留全部4个目标词，而不是只改变标题。首次AI版本已经包含此扩展。|
|2|只有造句增加fill模式|提供有语境的填空，四个HSK4目标词都有完整例句。首次扩展含此功能；当前版通过replace真正把目标词挖空。|
|3|修复9月按周整理后残留的weekpath引用，恢复统一导入与根目录路径|旧CLI传了out所以看似可运行；函数省略out会NameError。当前版直接调用两种函数和从临时目录运行都测试。|
|4|筛选条件两边统一str并strip|原版本只转换level，输入中整数或前后空格可能不匹配。应用列表推导式与字符串处理，测试同一等级的字符串/整数输入。|
|5|读取编码由utf-8改为utf-8-sig，保留newline空串|兼容电子表格导出的BOM，不让首列表头多出不可见字符；用带BOM的临时CSV验证。|
|6|默认输出回到根目录，增加--output指定额外结果|遵循课程路径约定，分组与填空结果可同时留存，不互相覆盖。|
|7|没有填空模板时不再输出含答案的伪填空|明确写“暂无语境填空模板”，退回造句题；五级词表可验证此边界。|

以上是实际代码修改记录，区分教师已有功能、9月AI扩展和当前修复，不能把教师已有utf-8和统计函数冒称为个人新增。

### 官方教程写法对应

- [列表与字典](https://docs.python.org/zh-cn/3/tutorial/datastructures.html)：列表推导式用于筛选；字典列表用于分组。`setdefault`返回已有列表或新建空列表，再append词条。
- [文件读写](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html)：with管理文件，写出明确编码。BOM兼容属于对输入边界的补充。

当前代码应用上述写法；阅读理解与课堂讲解需本人完成，不能用本段替代个人学习确认。

## 4. 最终版与初版差异说明

完整最终代码见[主程序](week03_Python/vocab_tool.py)，机器生成差异见[diff](week03_Python/evidence/initial_to_final.diff)。最终版保留四步处理，修复默认路径，规范等级比较，兼容BOM，允许指定输出，并避免把无例句的词伪装成有效填空。

教师讲义的样例终端写14词，仓库实际CSV有13条数据，程序按真实文件输出13，不为了对齐截图改写结果。等级4共4词：把字句、商量、感动、坚持；词性为名词1、动词3。

### 四个核心函数的解释

1. load_words：DictReader把每行映射成字典，表头成为键。
2. filter_by_level：遍历全部词条，仅保留等级匹配的项，不修改原列表。
3. count_by_pos：每看到一种词性，将其计数加一。
4. gen_grouped_exercises：先按词性分组，再逐条把练习写入文件；fill分支先取完整例句，再挖去目标词。

### 调试复盘

旧代码中的NameError说明名字未定义，定位到默认out分支可发现weekpath未导入。只测试CLI无法发现该分支，所以本次测试同时覆盖函数默认参数和命令行路径。验证记录见[验证记录](week03_Python/验证记录.md)。
