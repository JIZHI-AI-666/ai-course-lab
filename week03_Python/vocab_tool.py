"""从生词表 CSV 自动生成 HSK 词汇练习。

运行：python week03_Python/vocab_tool.py
填空模式：python week03_Python/vocab_tool.py --mode fill
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import weekpath  # noqa: E402

DATA = weekpath.data_path("生词表.csv")


def load_words(path=DATA):
    """读取 UTF-8 编码的生词 CSV。"""
    with open(path, encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def filter_by_level(words, level="4"):
    """筛选指定 HSK 等级的词条。"""
    return [word for word in words if word["HSK等级"] == str(level)]


def count_by_pos(words):
    """统计每种词性对应的词条数量。"""
    counts = {}
    for word in words:
        counts[word["词性"]] = counts.get(word["词性"], 0) + 1
    return counts


def group_by_pos(words):
    """按词性把词条归类，便于分组复习。"""
    groups = {}
    for word in words:
        groups.setdefault(word["词性"], []).append(word)
    return groups


def gen_grouped_exercises(words, out=None):
    """生成按词性分组的造句练习。"""
    out = Path(out) if out else weekpath.root_path("练习.txt")
    with open(out, "w", encoding="utf-8") as file:
        file.write("HSK 词汇分组造句练习\n")
        file.write("=" * 24 + "\n\n")
        for pos, group in group_by_pos(words).items():
            file.write("【%s】\n" % pos)
            for word in group:
                file.write("- 用“%s”造一个句子。（释义：%s）\n" %
                           (word["词汇"], word["释义"]))
            file.write("\n")


SENTENCE_TEMPLATES = {
    "把字句": "老师正在讲解____的用法。",
    "商量": "这件事我们明天再一起____吧。",
    "感动": "电影中的故事让我十分____。",
    "坚持": "学习汉语要每天____练习。",
}


def gen_fill_blank_exercises(words, out=None):
    """用目标词替换句子中的对应位置，生成填空题。"""
    out = Path(out) if out else weekpath.root_path("练习.txt")
    with open(out, "w", encoding="utf-8") as file:
        file.write("HSK 词汇填空练习\n")
        file.write("=" * 24 + "\n\n")
        for index, word in enumerate(words, start=1):
            sentence = SENTENCE_TEMPLATES.get(
                word["词汇"], "请用“____”完成一个与“%s”有关的句子。" % word["词汇"]
            )
            file.write("%d. %s（提示：%s）\n" %
                       (index, sentence, word["释义"]))


def main():
    parser = argparse.ArgumentParser(description="从生词表生成 HSK 词汇练习")
    parser.add_argument("--mode", choices=("group", "fill"), default="group",
                        help="group：按词性分组造句（默认）；fill：生成填空题")
    parser.add_argument("--level", default="4", help="要生成的 HSK 等级，默认 4")
    args = parser.parse_args()

    words = load_words()
    selected_words = filter_by_level(words, args.level)
    print("总词汇 %d 个，其中 HSK%s 词汇 %d 个，词性分布：%s" %
          (len(words), args.level, len(selected_words), count_by_pos(selected_words)))

    output = weekpath.root_path("练习.txt")
    if args.mode == "fill":
        gen_fill_blank_exercises(selected_words, output)
    else:
        gen_grouped_exercises(selected_words, output)
    print("已生成：%s" % output)


if __name__ == "__main__":
    main()
