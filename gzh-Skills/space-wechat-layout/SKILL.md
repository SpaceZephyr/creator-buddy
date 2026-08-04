---
name: space-wechat-layout
description: 微信公众号排版。Use when the user asks to turn an article, Markdown draft, longform post, essay, newsletter, review, or Chinese article into a WeChat Official Account-ready HTML layout with local preview, selectable Claude/OpenAI/Google-inspired styles, and a button to copy rich HTML for pasting into the WeChat editor.
---

# 微信公众号排版

Create a local HTML preview page that renders a provided article as WeChat-compatible rich HTML and includes a “复制 HTML” button. Preserve the article's meaning and content; only make light structural adjustments for layout readability.

## 公众号配图适配

**定位**：这是公众号「整篇视觉/排版」这一路——用户给文章内容，你输出可直接贴进公众号编辑器的 **HTML 排版**（`复制 HTML` 一键搬运）。是本集合里配图 Skill 的搭档：`space-chart-image` / `space-text-logic-diagram` 出**单张配图**，本 Skill 出**整篇排版**。

**输出**：默认 HTML（本 Skill 主路径）。需要把某个区块（如头图/金句卡）导出成图片时，对该区块截图导出 PNG，或交给 Codex/workbuddy 内置出图模型重绘。

**内容不改写**：只做排版层面的轻调整，保留全部事实、顺序、引用、结论。

## Workflow

1. **Collect the article**
   - If the user has not provided the article, ask them to paste it.
   - Detect title from the first `#` heading or first strong title-like line. If unclear, ask for a title.

2. **Ask for style**
   - Ask which style to use unless the user already specified one:
     - `Claude`: warm off-white, calm editorial, restrained borders, generous whitespace.
     - `OpenAI`: crisp white, black/gray, utilitarian documentation feel.
     - `Google`: bright white, soft blue/green/yellow/red accents, modular cards.
   - If the user says “你来定”, choose based on content:
     - reflective/narrative/opinion → Claude
     - technical/tutorial/product notes → OpenAI
     - data/list/comparison/education → Google
   - Read `references/style-guide.md` only when implementing the chosen style or when comparing styles.

3. **Prepare the content**
   - Do not rewrite the article substantially.
   - Keep all facts, order, quotes, scores, names, and conclusions intact.
   - Allow only layout-oriented optimization:
     - normalize heading levels;
     - split very long paragraphs;
     - convert obvious tables/lists into styled HTML tables/cards;
     - wrap long body sections in scrollable preview windows if the user asks or if a section is very long.

4. **Build the local preview**
   - Prefer a single static `index.html` when possible.
   - If working inside an existing Vite/front-end app, follow the app's current structure instead of creating a separate stack.
   - Include:
     - a top toolbar;
     - a `复制 HTML` button;
     - a visible status message after copying;
     - a centered WeChat content preview (`max-width: 677px`);
     - responsive mobile layout.
   - The copied payload must be the inner article HTML, not the whole app chrome.

5. **Copy behavior**
   - Use the Clipboard API with both `text/html` and `text/plain`.
   - Fall back to selecting the preview node and `document.execCommand("copy")`.
   - Button text must be clear: `复制 HTML` or `复制到公众号`.

6. **WeChat HTML constraints**
   - Use inline styles inside the copied article HTML.
   - Avoid external CSS, scripts, web fonts, CSS variables, SVG-only essential content, and interactive controls inside the copied article.
   - Keep cards at `border-radius: 8px` or less unless the chosen style specifically needs smaller corners.
   - Use simple semantic blocks: `section`, `h1`, `h2`, `h3`, `p`, `table`, `blockquote`.
   - For scrollable essay/body windows, inline style the article section with `max-height` and `overflow-y:auto`; keep headings, score summaries, and conclusions outside the scroll window.

7. **Verify**
   - Run the project build command if available.
   - Start or reuse a local dev server.
   - Confirm the local URL responds.
   - If Browser is available and stable, visually inspect the page; otherwise report build/server verification.

## Output Shape

Create or update files in the current project. For a plain static page, use:

```text
wechat-layout-output/
├── index.html
└── assets/        # only if local images are needed
```

For an existing app, update the app's normal entry files and keep the server URL unchanged when feasible.

## Default Preview Shell

The preview page should include this behavior, adapted to the project:

```js
async function copyArticleHtml(articleNode, statusNode) {
  const html = articleNode.innerHTML;
  const text = articleNode.innerText;
  try {
    await navigator.clipboard.write([
      new ClipboardItem({
        "text/html": new Blob([html], { type: "text/html" }),
        "text/plain": new Blob([text], { type: "text/plain" }),
      }),
    ]);
    statusNode.textContent = "已复制 HTML，可以粘贴到公众号正文区域。";
  } catch {
    const range = document.createRange();
    range.selectNode(articleNode);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    document.execCommand("copy");
    selection.removeAllRanges();
    statusNode.textContent = "已用兼容模式复制当前预览内容。";
  }
}
```

## Final Response

Tell the user:
- the local preview URL;
- which style was used;
- which files were created or changed;
- how to copy and paste into WeChat;
- any verification that passed or could not be run.
