"""回归默认输出、CSV 编码与两种练习模式；不使用网络。"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('vocab_tool', Path(__file__).with_name('vocab_tool.py'))
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class VocabTests(unittest.TestCase):
    def test_course_data_and_counts(self):
        words=V.load_words()
        selected=V.filter_by_level(words,4)
        self.assertEqual(len(words),13)
        self.assertEqual({w['词汇'] for w in selected},{'把字句','商量','感动','坚持'})
        self.assertEqual(V.count_by_pos(selected),{'名词':1,'动词':3})

    def test_level_types_and_spaces(self):
        words=[{'HSK等级':4},{'HSK等级':' 4 '},{'HSK等级':'5'}]
        self.assertEqual(len(V.filter_by_level(words,'4')),2)

    def test_bom_csv(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'词.csv'
            p.write_text('词汇,HSK等级,词性,释义\n坚持,4,动词,不放弃\n',encoding='utf-8-sig')
            self.assertEqual(V.load_words(p)[0]['词汇'],'坚持')

    def test_default_out_works_for_both_functions(self):
        words=V.filter_by_level(V.load_words())
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'练习.txt'
            with patch.object(V.weekpath,'root_path',return_value=str(p)):
                V.gen_grouped_exercises(words)
                self.assertIn('【动词】',p.read_text())
                V.gen_fill_blank_exercises(words)
                self.assertEqual(p.read_text().count('____'),4)

    def test_unknown_template_is_not_fake_blank(self):
        word={'词汇':'愚公移山','HSK等级':'5','词性':'成语','释义':'坚持不懈'}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'练习.txt';V.gen_fill_blank_exercises([word],p)
            self.assertIn('暂无语境填空模板',p.read_text())
            self.assertNotIn('____',p.read_text())


if __name__=='__main__':unittest.main()
