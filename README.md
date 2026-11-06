# coursebook

把课程笔记写成一本书：**单文件 HTML，公式离线渲染，可搜索、可打印、可发布**。

不是某个课程的资料，而是一个工具：你写 Markdown，它生成一份 4 MB 左右、双击就能打开的手册。

```
笔记 (Markdown)  →  coursebook build  →  index.html（样式/脚本/公式/插图全内联）
                                            ├─ 浏览器直接看
                                            ├─ 打印成 PDF
                                            └─ 推到 GitHub Pages
```

![示例](docs/screenshot.png)

## 为什么又造一个轮子

现成方案里，Markdown → 网页的工具很多，但少有同时满足这四条的：

| 需求 | Word / PDF | 笔记软件 | MkDocs 类 | coursebook |
|---|---|---|---|---|
| 公式排版 | 长文档易错位 | 看平台 | 需要配置 | MathJax 离线渲染 |
| 离线打开 | 要装软件 | 要登录 | 要起服务 | 单文件双击 |
| 打印成书 | 分页难控 | 差 | 一般 | 专门写过 `@media print` |
| 搜索 | 看软件 | 有 | 有 | 内置，无需服务 |

目标很具体：**考前两周，图书馆没网、只有手机、最后一定要打印**。

## 快速开始

```bash
git clone https://github.com/Nothankther/coursebook
cd coursebook
pip install -e .

coursebook new my-course --title "我的课程复习手册"
cd my-course
coursebook build
coursebook serve        # 打开 http://127.0.0.1:8765 预览
```

生成的结构：

```
my-course/
├── book.json            # 标题、副标题、侧栏角标
├── src/
│   ├── 00-hero.html     # 封面（原始 HTML，随意改）
│   └── 01-chapter.md    # 章节模板，复制成 02、03……
├── assets/              # 放 fig-*.svg
└── index.html           # 构建产物
```

`coursebook build` 会把 `src/` 下所有文件按文件名排序拼接；`NN-` 前缀决定章节序号，`00-` 开头视为封面、不套章节壳。

仓库里的 `examples/demo` 就是一个能直接构建的最小项目：

```bash
cd examples/demo && coursebook build
```

## 写作语法

标准 Markdown 的一个子集，外加四个课程笔记常用的扩展。

| 写法 | 效果 |
|---|---|
| `# 第一章 标题` | 章节标题（自动进目录） |
| `> 一句话` （紧跟在标题后） | 章节导语，显示在标题下方 |
| `<!-- short: ① 短名 -->` | 目录里的短标题 |
| `$...$` / `$$...$$` | 行内 / 独立公式，交给 MathJax |
| `<!--FIG:name-->` | 内联 `assets/fig-name.svg` |
| `::: tip 标题` … `:::` | 提示盒 |
| `::: example 例 1-1 \| 标题` … `---` … `:::` | 折叠例题（`---` 前是题干，后是解答） |
| `\| 表头 \|` + `\|---\|` | 表格 |

盒子有五种：`tip`（提示）、`key`（重点）、`warn`（易错）、`def`（定义）、`mem`（记忆）。

完整语法见 [docs/writing.md](docs/writing.md)，组件清单见 [docs/components.md](docs/components.md)。

## 内置能力

- **目录**：自动生成，滚动高亮，可勾选“已复习”，进度存本地。
- **搜索**：按 `/` 聚焦，输入即出结果，摘要取排版后的正文。
- **折叠例题**：默认收起，打印前自动展开。
- **打印**：隐藏侧栏与工具条、表格跨页重复表头、块内不分页。
- **移动端**：侧栏抽屉化，公式自动缩放。

## 导出 PDF

用 Edge / Chrome 的无头模式打印，`--virtual-time-budget` 要给足，否则 MathJax 没排完：

```bash
msedge --headless --disable-gpu \
  --print-to-pdf="手册.pdf" --no-pdf-header-footer \
  --virtual-time-budget=40000 "file:///绝对路径/index.html"
```

## 发布到 GitHub Pages

`coursebook new` 已经生成 `.github/workflows/pages.yml`。把项目推到 GitHub，在 **Settings → Pages → Source** 选 **GitHub Actions**，之后每次 push 自动部署。

## 设计取舍

- **单文件而不是多页**：体积换便携。4 MB 换来“发给任何人双击就能看”，值。
- **Markdown 而不是所见即所得**：写公式和表格时，纯文本比富文本编辑器快得多。
- **不做账号、不做云同步**：笔记属于本地。需要分享就发文件或开 Pages。
- **不内置 PDF 生成**：浏览器打印比任何库都更懂分页与字体。

## 已知限制

- 单文件 4 MB，首次排版约 2 秒；公式极多时会更慢。
- Markdown 只实现了常用子集，复杂排版请直接写 HTML（`.html` 文件会原样插入）。
- 不支持多人协作编辑（这不是它的目标）。
- 打印分页需要人工检查一遍，尤其是长表格与跨页插图。

## Roadmap

- [ ] `coursebook export`：调用本机浏览器一键出 PDF
- [ ] 交互组件注册机制（拖动、滑块、图表）
- [ ] 主题切换（目前只有浅色）
- [ ] 英文文档

## License

MIT。用它做的笔记归你自己。
