# -*- coding: utf-8 -*-
"""一个够用的 Markdown 子集渲染器。

只依赖标准库，支持写课程笔记需要的那些语法：

    # 标题 / ## 小节 / ### 小标题
    段落、**加粗**、*斜体*、`行内代码`
    - 无序列表 / 1. 有序列表
    > 引用
    | 表格 | 两列 |
    ```代码块```
    $行内公式$ 与 $$独立公式$$（原样保留，交给 MathJax）
    ::: tip 标题 ... :::        提示盒，type 可为 tip/key/warn/def/mem
    ::: example 例 1-1 | 标题 ... --- ... :::   折叠例题
    ::: quiz 自测 ... :::        折叠自测
    以 < 开头的行按原始 HTML 原样输出（需要精细排版时用）
"""
import re

MATH = re.compile(r'\$\$[\s\S]*?\$\$|\$[^$\n]*?\$')
CODE = re.compile(r'`([^`\n]+)`')


def _inline(text):
    """行内格式：先摘出公式与代码，避免被转义或二次处理。"""
    keep = []

    def stash(m):
        keep.append(m.group(0))
        return '\x00%d\x00' % (len(keep) - 1)

    text = MATH.sub(stash, text)
    text = CODE.sub(lambda m: stash_code(m, keep), text)

    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)', r'<img src="\2" alt="\1">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', text)

    def restore(m):
        return keep[int(m.group(1))]

    return re.sub(r'\x00(\d+)\x00', restore, text)


def stash_code(m, keep):
    keep.append('<code>%s</code>' % m.group(1).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
    return '\x00%d\x00' % (len(keep) - 1)


def _is_table_sep(line):
    return bool(re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]*$', line)) and '-' in line


def _split_row(line):
    cells = line.strip().strip('|').split('|')
    return [c.strip() for c in cells]


def render(text, in_box=False):
    lines = text.replace('\r\n', '\n').split('\n')
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        # 代码块
        if s.startswith('```'):
            lang = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            code = '\n'.join(buf).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            cls = ' class="language-%s"' % lang if lang else ''
            out.append('<pre><code%s>%s</code></pre>' % (cls, code))
            continue

        # ::: 容器
        if s.startswith(':::'):
            head = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith(':::'):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append(_container(head, '\n'.join(buf)))
            continue

        # 分隔线
        if re.match(r'^-{3,}$', s):
            out.append('<hr>')
            i += 1
            continue

        # 标题（盒子内降一级，避免破坏文档层级）
        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            lv = len(m.group(1)) + (1 if in_box else 0)
            lv = min(lv, 6)
            out.append('<h%d>%s</h%d>' % (lv, _inline(m.group(2)), lv))
            i += 1
            continue

        # 原始 HTML 块
        if s.startswith('<'):
            buf = []
            while i < n and lines[i].strip():
                buf.append(lines[i])
                i += 1
            out.append('\n'.join(buf))
            continue

        # 表格
        if '|' in s and i + 1 < n and _is_table_sep(lines[i + 1]):
            head = _split_row(s)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                rows.append(_split_row(lines[i]))
                i += 1
            html = ['<div class="tbl-wrap"><table class="tbl">', '<thead><tr>']
            html += ['<th>%s</th>' % _inline(c) for c in head]
            html.append('</tr></thead><tbody>')
            for r in rows:
                html.append('<tr>' + ''.join('<td>%s</td>' % _inline(c) for c in r) + '</tr>')
            html.append('</tbody></table></div>')
            out.append(''.join(html))
            continue

        # 引用
        if s.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append('<blockquote><p>%s</p></blockquote>' % _inline(' '.join(buf)))
            continue

        # 列表
        if re.match(r'^[-*]\s+', s):
            items = []
            while i < n and re.match(r'^[-*]\s+', lines[i].strip()):
                items.append(_inline(re.sub(r'^[-*]\s+', '', lines[i].strip())))
                i += 1
            out.append('<ul>' + ''.join('<li>%s</li>' % x for x in items) + '</ul>')
            continue
        if re.match(r'^\d+\.\s+', s):
            items = []
            while i < n and re.match(r'^\d+\.\s+', lines[i].strip()):
                items.append(_inline(re.sub(r'^\d+\.\s+', '', lines[i].strip())))
                i += 1
            out.append('<ol>' + ''.join('<li>%s</li>' % x for x in items) + '</ol>')
            continue

        # 段落
        buf = [s]
        i += 1
        while i < n:
            t = lines[i].strip()
            if (not t or t.startswith('#') or t.startswith(':::') or t.startswith('```')
                    or t.startswith('>') or t.startswith('<') or t.startswith('|')
                    or re.match(r'^[-*]\s+', t) or re.match(r'^\d+\.\s+', t)
                    or re.match(r'^-{3,}$', t)):
                break
            buf.append(t)
            i += 1
        out.append('<p>%s</p>' % _inline(' '.join(buf)))

    return '\n'.join(out)


def _container(head, body):
    parts = head.split(None, 1)
    kind = parts[0] if parts else 'tip'
    title = parts[1] if len(parts) > 1 else ''

    if kind == 'example':
        lv, _, name = title.partition('|')
        lv = lv.strip() or '例'
        name = name.strip() or '例题'
        q, _, sol = body.partition('\n---\n')
        return ('<div class="example"><div class="ex-head"><span class="lv">%s</span><b>%s</b></div>'
                '<div class="q">%s</div>'
                '<details><summary>展开解答</summary><div class="sol">%s</div></details></div>'
                % (_inline(lv), _inline(name), render(q, in_box=True), render(sol, in_box=True)))

    if kind == 'quiz':
        return ('<div class="quiz"><div class="q">%s</div>'
                '<button class="toggle">查看答案</button><div class="ans">%s</div></div>'
                % (render(body, in_box=True), '<p>把 ::: quiz 换成 ::: example，或在正文里写答案。</p>'))

    cls = kind if kind in ('tip', 'key', 'warn', 'def', 'mem') else 'tip'
    t = '<div class="t">%s</div>' % _inline(title) if title else ''
    return '<div class="box %s">%s%s</div>' % (cls, t, render(body, in_box=True))
