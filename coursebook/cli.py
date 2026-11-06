# -*- coding: utf-8 -*-
"""命令行入口：coursebook new / build / serve。"""
import argparse
import http.server
import os
import shutil
import socketserver
import sys
import webbrowser

from .builder import build

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, 'template')


def cmd_new(args):
    target = os.path.abspath(args.dir)
    if os.path.exists(target) and os.listdir(target):
        raise SystemExit('目录非空: %s' % target)
    shutil.copytree(TEMPLATE, target)
    os.makedirs(os.path.join(target, 'assets'), exist_ok=True)
    book = os.path.join(target, 'book.json')
    with open(book, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('__TITLE__', args.title or os.path.basename(target))
    with open(book, 'w', encoding='utf-8') as f:
        f.write(text)
    print('已创建 %s' % target)
    print('下一步:')
    print('  cd %s' % target)
    print('  coursebook build')
    print('  coursebook serve')


def cmd_build(args):
    build(os.path.abspath(args.dir), offline=args.offline)


def cmd_serve(args):
    root = os.path.abspath(args.dir)
    index = os.path.join(root, 'index.html')
    if not os.path.exists(index):
        build(root, offline=args.offline)
    os.chdir(root)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, fmt, *a):
            pass

    with socketserver.TCPServer(('127.0.0.1', args.port), Handler) as httpd:
        url = 'http://127.0.0.1:%d/' % args.port
        print('预览 %s  （Ctrl+C 结束）' % url)
        if not args.no_open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


def main(argv=None):
    ap = argparse.ArgumentParser(prog='coursebook', description='把课程笔记变成单文件 HTML 复习手册')
    sub = ap.add_subparsers(dest='cmd')

    p = sub.add_parser('new', help='新建一个手册项目')
    p.add_argument('dir')
    p.add_argument('--title', default=None)
    p.set_defaults(func=cmd_new)

    p = sub.add_parser('build', help='构建 index.html')
    p.add_argument('dir', nargs='?', default='.')
    p.add_argument('--offline', action='store_true', help='不下载 MathJax（无网络时用）')
    p.set_defaults(func=cmd_build)

    p = sub.add_parser('serve', help='本地预览')
    p.add_argument('dir', nargs='?', default='.')
    p.add_argument('--port', type=int, default=8765)
    p.add_argument('--no-open', action='store_true')
    p.add_argument('--offline', action='store_true')
    p.set_defaults(func=cmd_serve)

    args = ap.parse_args(argv)
    if not getattr(args, 'func', None):
        ap.print_help()
        return 0
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
