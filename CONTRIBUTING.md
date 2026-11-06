# Contributing

欢迎 issue 与 PR。这个项目的目标很窄：**让课程笔记变成一份能离线看、能打印的单文件手册**。超出这个范围的功能（云同步、账号、多人协作）不会合入。

## 本地开发

```bash
git clone https://github.com/Nothankther/coursebook
cd coursebook
pip install -e .
python -m unittest discover -s tests
```

改完代码用示例项目验证：

```bash
cd examples/demo
coursebook build
coursebook serve
```

## 提交前检查

1. `python -m unittest discover -s tests` 全绿；
2. 用示例项目构建一次，页面无 `$` 泄漏、无 `data-mjx-error`；
3. 打印预览（Ctrl+P）检查分页：例题不被截断、表头跨页重复。

## 代码约定

- 只依赖 Python 标准库，不引第三方包；
- 生成的 HTML 必须保持单文件、无外部请求；
- 新增 Markdown 语法时，同步更新 `docs/writing.md` 与测试。

## 报告问题

请附上：最小复现的 Markdown 片段、`coursebook build` 的输出、浏览器版本。
