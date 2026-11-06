# 组件清单

所有组件都是纯 CSS 类，不依赖 JavaScript，打印时保持原样。

## 提示盒

```markdown
::: tip 记忆提示
内容
:::
```

| 类型 | 语义 | 颜色 |
|---|---|---|
| `tip` | 提示、技巧 | 青 |
| `key` | 重点结论 | 蓝 |
| `warn` | 易错、警告 | 红 |
| `def` | 定义 | 紫 |
| `mem` | 记忆口诀 | 绿 |

盒子内可以放段落、列表、公式、表格。

## 例题

```markdown
::: example 例 2-1 | 结构图化简
题干……
---
解答……
:::
```

渲染为带编号的卡片，解答放在 `<details>` 里，默认收起。标题里 `|` 前是编号，后是名称。

## 自测

```markdown
::: quiz 自测
题目……
答案……
:::
```

## 公式块

```html
<div class="formula">
  <p>$$G_c(s)=\frac{aTs+1}{Ts+1}$$</p>
  <div class="cap">公式下方的说明</div>
</div>
```

## 表格

Markdown 表格自动套 `.tbl` 样式。需要固定表头、跨页重复时，构建后的表格已带 `thead`，打印时自动重复。

## 章节标记

构建器生成的结构：

```html
<section class="chapter" id="c3" data-num="3"
         data-title="第三章 时域分析法" data-short="③ 时域">
  <div class="wrap">
    <div class="ch-head">
      <div class="ch-no"><b>03</b> CHAPTER</div>
      <h2>标题<span class="en">English</span></h2>
      <p class="ch-desc">导语</p>
    </div>
    ...
  </div>
</section>
```

目录、搜索、进度都依赖 `data-num` / `data-title` / `data-short`，手写 HTML 章节时请保留。

## 打印相关

- `.no-print`：打印时隐藏（工具条已用）。
- `figure`、`.box`、`.tbl tr`：`break-inside: avoid`，避免从中间断开。
- `table.tbl thead`：`display: table-header-group`，跨页重复表头。
- `<details>`：打印前由脚本全部展开，同时 CSS 强制 `.sol { display: block }`。
