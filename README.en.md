# coursebook

Turn course notes into a book: **a single HTML file, offline formulas, searchable and printable**.

Not a set of notes for one course — a tool. You write Markdown; it produces a ~4 MB handbook that opens with a double click.

```
notes (Markdown)  →  coursebook build  →  index.html  (styles, scripts, formulas, figures inlined)
                                            ├─ open in any browser
                                            ├─ print to PDF
                                            └─ deploy to GitHub Pages
```

![screenshot](docs/screenshot.png)

## Why another tool

Plenty of Markdown-to-HTML generators exist. Few satisfy all four requirements at once:

| Requirement | Word / PDF | Note apps | MkDocs-like | coursebook |
|---|---|---|---|---|
| Formula typesetting | drifts in long docs | platform-dependent | needs config | MathJax, offline |
| Open without setup | needs an app | needs an account | needs a server | one file, double click |
| Print as a book | page breaks are hard | poor | average | dedicated `@media print` |
| Search | app-dependent | yes | yes | built in, no server |

The target is concrete: **two weeks before an exam, no network in the library, only a phone, and it has to be printed anyway**.

## Quick start

```bash
git clone https://github.com/Nothankther/coursebook
cd coursebook
pip install -e .

coursebook new my-course --title "My Course Handbook"
cd my-course
coursebook build
coursebook serve        # http://127.0.0.1:8765
```

Layout:

```
my-course/
├── book.json            # title, subtitle, sidebar badge
├── src/
│   ├── 00-hero.html     # cover (plain HTML, edit freely)
│   └── 01-chapter.md    # chapter template; copy to 02, 03, ...
├── assets/              # put fig-*.svg here
└── index.html           # build output
```

`coursebook build` concatenates everything under `src/` in filename order. The `NN-` prefix sets the chapter number; files starting with `00-` are treated as a cover and are not wrapped in a chapter shell.

A minimal project ships in [`examples/demo`](examples/demo):

```bash
cd examples/demo && coursebook build
```

## Syntax

A subset of Markdown plus four extensions useful for course notes.

| Syntax | Result |
|---|---|
| `# Chapter title` | chapter heading, added to the TOC |
| `> one line` right after the title | chapter lede, rendered under the heading |
| `<!-- short: ③ Short name -->` | short label in the sidebar |
| `$...$` / `$$...$$` | inline / display math, rendered by MathJax |
| `<!--FIG:name-->` | inline `assets/fig-name.svg` |
| `::: tip Title` … `:::` | callout box |
| `::: example 例 1-1 \| Title` … `---` … `:::` | collapsible worked example (`---` splits problem and solution) |
| `\| header \|` + `\|---\|` | table |

Five box types: `tip`, `key`, `warn`, `def`, `mem`.

Full syntax in [docs/writing.md](docs/writing.md); component reference in [docs/components.md](docs/components.md).

## Built in

- **Table of contents** — generated, scroll-spy highlight, per-chapter “reviewed” checkbox stored locally.
- **Search** — press `/`, type, get results; snippets come from typeset text, not LaTeX source.
- **Collapsible examples** — closed by default, expanded automatically before printing.
- **Print** — sidebar and toolbar hidden, table headers repeat across pages, blocks avoid page breaks.
- **Mobile** — sidebar becomes a drawer, formulas scale down.

## Export to PDF

Print with headless Edge / Chrome. Give `--virtual-time-budget` enough time, otherwise MathJax has not finished typesetting:

```bash
msedge --headless --disable-gpu \
  --print-to-pdf="handbook.pdf" --no-pdf-header-footer \
  --virtual-time-budget=40000 "file:///absolute/path/index.html"
```

## Deploy to GitHub Pages

`coursebook new` already writes `.github/workflows/pages.yml`. Push the project, then set **Settings → Pages → Source** to **GitHub Actions**.

## Design decisions

- **Single file over multi-page**: size buys portability. 4 MB for “send it to anyone and it opens” is a fair trade.
- **Markdown over WYSIWYG**: formulas and tables are faster to type than to click.
- **No accounts, no cloud sync**: notes stay local. Share a file or turn on Pages.
- **No built-in PDF renderer**: the browser understands pagination and fonts better than any library.

## Known limitations

- A 4 MB file takes about two seconds for the first typeset; formula-heavy books are slower.
- Only a common Markdown subset is implemented. For complex layouts, write HTML — `.html` files are inserted as-is.
- No collaborative editing (not a goal).
- Page breaks deserve a manual check, especially long tables and full-page figures.

## Roadmap

- [ ] `coursebook export`: one command to render PDF through the local browser
- [ ] Interactive component registry (sliders, drag-and-drop diagrams)
- [ ] Dark theme
- [ ] Chinese docs are the primary set; this file is the English mirror

## License

MIT. The notes you write are yours.
