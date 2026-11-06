# -*- coding: utf-8 -*-
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from coursebook import md
from coursebook.builder import build


class TestMarkdown(unittest.TestCase):
    def test_heading_and_paragraph(self):
        html = md.render('# 标题\n\n正文 $x<1$ 结束')
        self.assertIn('<h1>标题</h1>', html)
        self.assertIn('$x<1$', html)

    def test_box(self):
        html = md.render('::: warn 易错\n别写 &lt;\n:::')
        self.assertIn('class="box warn"', html)
        self.assertIn('易错', html)

    def test_example(self):
        html = md.render('::: example 例 1-1 | 一阶\n题干\n---\n解答\n:::')
        self.assertIn('class="example"', html)
        self.assertIn('<details>', html)
        self.assertIn('解答', html)

    def test_table(self):
        html = md.render('| a | b |\n|---|---|\n| 1 | 2 |')
        self.assertIn('<table class="tbl">', html)
        self.assertIn('<td>1</td>', html)

    def test_bold_and_code(self):
        html = md.render('**粗** 与 `a<b`')
        self.assertIn('<strong>粗</strong>', html)
        self.assertIn('<code>a&lt;b</code>', html)


class TestBuild(unittest.TestCase):
    def test_demo_builds(self):
        src = os.path.join(ROOT, 'examples', 'demo')
        tmp = tempfile.mkdtemp()
        try:
            dst = os.path.join(tmp, 'demo')
            shutil.copytree(src, dst)
            out = build(dst, offline=True)
            self.assertTrue(os.path.exists(out))
            with open(out, encoding='utf-8') as f:
                html = f.read()
            self.assertIn('<title>', html)
            self.assertIn('class="chapter"', html)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
