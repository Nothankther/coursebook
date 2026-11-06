# -*- coding: utf-8 -*-
"""把 src/ 下的 Markdown / HTML 章节组装成一个单文件 index.html。"""
import glob
import io
import json
import os
import re
import sys
import urllib.request

from . import md

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
CACHE = os.path.join(os.path.expanduser('~'), '.coursebook')
MATHJAX_CDN = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'

MJ_CFG = r"""
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    tags: 'none',
    macros: { deg: '^{\\circ}', dd: '{\\mathrm{d}}', j: '{\\mathrm{j}}', e: '{\\mathrm{e}}' }
  },
  svg: { fontCache: 'global', scale: 1.02 },
  options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] },
  startup: { typeset: true }
};
"""

TEMPLATE = u"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<style>__CSS__</style>
<script>__MJCFG__</script>
__MATHJAX__
</head>
<body>
<div id="progress"></div>
<button id="menuBtn" aria-label="目录"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#334155" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>
<aside id="sidebar">
  <div class="brand">
    <div class="mark"><div class="dot">__BRAND__</div><h1>__TITLE__</h1></div>
    <p>__SUB__</p>
  </div>
  <div class="searchbox">
    <div class="wrap">
      <svg class="icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
      <input id="q" type="text" placeholder="搜索章节 / 公式 / 关键词" autocomplete="off">
      <kbd>/</kbd>
    </div>
  </div>
  <nav id="toc"></nav>
  <div class="sidebar-foot">
    <span>已复习 <b class="ring" id="doneCount">0/0</b></span>
    <span class="ring" id="doneRing" style="width:18px;height:18px;border-radius:50%;display:inline-block;background:conic-gradient(#0f766e 0%,#e2e8f0 0%)"></span>
  </div>
</aside>
<main>
__BODY__
</main>
<div class="toolbar no-print">
  <button id="btnAll" title="展开 / 收起全部解答"><svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10"/></svg></button>
  <button id="btnPrint" title="打印 / 导出 PDF"><svg viewBox="0 0 24 24"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg></button>
  <button id="btnTop" title="回到顶部"><svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg></button>
</div>
<script>__JS__</script>
</body>
</html>
"""


def read(path):
    with io.open(path, 'r', encoding='utf-8') as f:
        return f.read()


def ensure_mathjax(project, offline=False):
    """优先用项目内的 MathJax；其次读缓存；最后下载；都不行就退回 CDN。"""
    local = os.path.join(project, 'assets', 'mathjax-tex-svg.js')
    if os.path.exists(local):
        return '<script>%s</script>' % read(local)
    cached = os.path.join(CACHE, 'mathjax-tex-svg.js')
    if os.path.exists(cached):
        return '<script>%s</script>' % read(cached)
    if not offline:
        try:
            os.makedirs(CACHE, exist_ok=True)
            print('· 下载 MathJax（仅首次，约 2 MB）')
            with urllib.request.urlopen(MATHJAX_CDN.replace('/es5/tex-svg.js', '/es5/tex-svg.js'), timeout=60) as r:
                data = r.read()
            with open(cached, 'wb') as f:
                f.write(data)
            return '<script>%s</script>' % data.decode('utf-8', 'replace')
        except Exception as e:
            print('· 下载失败（%s），改为引用 CDN。' % e)
            print('  如需离线使用：把 mathjax-tex-svg.js 放到项目的 assets/ 目录。')
    return '<script src="%s"></script>' % MATHJAX_CDN


def chapter_meta(path, text):
    fn = os.path.basename(path)
    m = re.match(r'^(\d+)[-_]', fn)
    num = int(m.group(1)) if m else 0
    short = re.search(r'<!--\s*short:\s*(.+?)\s*-->', text)
    en = re.search(r'<!--\s*en:\s*(.+?)\s*-->', text)
    cid = re.search(r'<!--\s*id:\s*([\w\-]+)\s*-->', text)
    title = None
    body = text
    h1 = re.search(r'^#\s+(.+)$', text, re.M)
    if h1:
        title = h1.group(1).strip()
        body = text[:h1.start()] + text[h1.end():]
    desc = ''
    bq = re.search(r'^\s*>\s*(.+)$', body, re.M)
    if bq:
        desc = bq.group(1).strip()
        body = body[:bq.start()] + body[bq.end():]
    body = re.sub(r'<!--[\s\S]*?-->', '', body)
    return {
        'num': num,
        'id': cid.group(1) if cid else ('c%d' % num if num else 'chapter'),
        'title': title or os.path.splitext(fn)[0],
        'short': (short.group(1) if short else (title or fn)),
        'en': en.group(1) if en else '',
        'desc': desc,
        'body': body.strip(),
    }


def wrap_chapter(meta, inner):
    en = '<span class="en">%s</span>' % meta['en'] if meta['en'] else ''
    desc = '<p class="ch-desc">%s</p>' % md._inline(meta['desc']) if meta['desc'] else ''
    return ('<section class="chapter" id="%s" data-num="%d" data-title="%s" data-short="%s">\n'
            '  <div class="wrap">\n'
            '    <div class="ch-head">\n'
            '      <div class="ch-no"><b>%02d</b> CHAPTER</div>\n'
            '      <h2>%s%s</h2>\n      %s\n    </div>\n%s\n  </div>\n</section>'
            % (meta['id'], meta['num'], meta['title'], meta['short'], meta['num'],
               md._inline(meta['title']), en, desc, inner))


def build(project, offline=False):
    book_path = os.path.join(project, 'book.json')
    book = {}
    if os.path.exists(book_path):
        book = json.loads(read(book_path))
    title = book.get('title', '课程复习手册')
    subtitle = book.get('subtitle', '')
    brand = book.get('brand', '复习')

    src = os.path.join(project, 'src')
    files = sorted(glob.glob(os.path.join(src, '*.md')) + glob.glob(os.path.join(src, '*.html')))
    if not files:
        raise SystemExit('src/ 下没有章节文件')

    chunks = []
    for f in files:
        text = read(f)
        if f.endswith('.md'):
            meta = chapter_meta(f, text)
            # 章内标题降一级：## 小节 → h3，避免与章节标题同级
            body = re.sub(r'^(#{2,5})\s', lambda m: '#' * (len(m.group(1)) + 1) + ' ', meta['body'], flags=re.M)
            inner = md.render(body)
            if meta['num'] == 0:
                chunks.append(inner)          # 00 开头：封面，不套章节壳
            else:
                chunks.append(wrap_chapter(meta, inner))
        else:
            chunks.append(text)

    body = '\n'.join(chunks)
    body = (body.replace('{{title}}', title).replace('{{subtitle}}', subtitle)
                .replace('{{brand}}', brand))

    def fig_sub(m):
        p = os.path.join(project, 'assets', 'fig-%s.svg' % m.group(1))
        return read(p) if os.path.exists(p) else '<!-- missing figure: %s -->' % m.group(1)

    body = re.sub(r'<!--FIG:([\w\-]+)-->', fig_sub, body)

    def esc_math(m):
        return m.group(0).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    body = re.sub(r'\$\$[\s\S]*?\$\$', esc_math, body)
    body = re.sub(r'\$[^$\n]*?\$', esc_math, body)

    css = read(os.path.join(ASSETS, 'style.css'))
    js = read(os.path.join(ASSETS, 'app.js'))
    mj = ensure_mathjax(project, offline)

    html = TEMPLATE
    for k, v in (('__TITLE__', title), ('__DESC__', subtitle), ('__SUB__', subtitle),
                 ('__BRAND__', brand), ('__CSS__', css), ('__MJCFG__', MJ_CFG),
                 ('__MATHJAX__', mj), ('__BODY__', body), ('__JS__', js)):
        html = html.replace(k, v)

    out = os.path.join(project, 'index.html')
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    size = os.path.getsize(out) / 1048576.0
    words = len(re.sub(r'<[^>]+>', '', body))
    print('built %s  %.2f MB  %d 字' % (out, size, words))
    return out
