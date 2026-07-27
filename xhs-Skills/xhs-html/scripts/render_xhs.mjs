#!/usr/bin/env node
/**
 * 渲染并检查单个小红书多页 HTML。
 *
 * 用法：
 *   node render_xhs.mjs --html index.html --out-dir /tmp/xhs-check
 *   node render_xhs.mjs --html index.html --out-dir /tmp/xhs-check --strict
 *   node render_xhs.mjs --html index.html --out-dir /tmp/xhs-check --guides
 *   node render_xhs.mjs --html index.html --out-dir /tmp/xhs-thumb --scale 0.25
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const WIDTH = 1080;
const HEIGHT = 1440;

function loadPlaywright() {
  try {
    return require("playwright");
  } catch {
    const roots = [
      ...(process.env.NODE_PATH || "").split(path.delimiter).filter(Boolean),
      path.join(
        os.homedir(),
        ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules",
      ),
    ];
    for (const root of roots) {
      try {
        return require(path.join(root, "playwright"));
      } catch {
        // Try the next known module root.
      }
    }
  }
  throw new Error(
    "找不到 playwright。请安装 npm i playwright，或在 Codex 工作区运行。",
  );
}

function parseArgs(argv) {
  const args = {
    selector: ".sheet",
    scale: 1,
    minPages: 6,
    guides: false,
    strict: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (key === "--guides") args.guides = true;
    else if (key === "--strict") args.strict = true;
    else if (key === "--html") args.html = argv[++i];
    else if (key === "--out-dir") args.outDir = argv[++i];
    else if (key === "--selector") args.selector = argv[++i];
    else if (key === "--scale") args.scale = Number(argv[++i]);
    else if (key === "--min-pages") args.minPages = Number(argv[++i]);
    else if (key === "--help" || key === "-h") {
      console.log(
        "node render_xhs.mjs --html index.html --out-dir /tmp/xhs-check " +
          "[--strict] [--guides] [--scale 0.25] [--min-pages 6]",
      );
      process.exit(0);
    } else {
      throw new Error(`未知参数：${key}`);
    }
  }
  if (!args.html || !args.outDir) {
    throw new Error("必须同时提供 --html 和 --out-dir");
  }
  if (!(args.scale > 0)) throw new Error("--scale 必须大于 0");
  if (!(args.minPages >= 1)) throw new Error("--min-pages 必须大于 0");
  return args;
}

const GUIDE_CSS = `
.sheet > .__xhs_guides__{
  position:absolute;
  left:80px;right:80px;top:100px;bottom:120px;
  z-index:999999;pointer-events:none;
  border:2px dashed rgba(255,0,80,.85);
}
.sheet > .__xhs_guides__::after{
  content:"安全区 80 / 100 / 80 / 120";
  position:absolute;left:4px;bottom:4px;
  padding:5px 8px;border-radius:6px;
  background:rgba(255,255,255,.9);color:#ff0050;
  font:500 20px/1 -apple-system,"PingFang SC",sans-serif;
}`;

function checkSheet(sheet) {
  const problems = [];
  const sr = sheet.getBoundingClientRect();
  const width = Math.round(sr.width);
  const height = Math.round(sr.height);
  if (width !== 1080 || height !== 1440) {
    problems.push(`尺寸为 ${width}×${height}，应为 1080×1440`);
  }
  if (sheet.scrollWidth > sheet.clientWidth + 2) {
    problems.push(`页面横向溢出 ${sheet.scrollWidth - sheet.clientWidth}px`);
  }
  if (sheet.scrollHeight > sheet.clientHeight + 2) {
    problems.push(`页面纵向溢出 ${sheet.scrollHeight - sheet.clientHeight}px`);
  }

  const escaped = [];
  sheet.querySelectorAll("*:not([data-allow-overflow])").forEach((el) => {
    const style = getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden") return;
    const r = el.getBoundingClientRect();
    if (
      r.left < sr.left - 1 ||
      r.right > sr.right + 1 ||
      r.top < sr.top - 1 ||
      r.bottom > sr.bottom + 1
    ) {
      const cls = typeof el.className === "string" ? el.className.trim() : "";
      escaped.push(cls ? `.${cls.replace(/\s+/g, ".")}` : el.tagName.toLowerCase());
    }
  });
  if (escaped.length) {
    problems.push(
      `有元素越出画布：${[...new Set(escaped)].slice(0, 6).join("、")}`,
    );
  }
  return problems;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const htmlPath = path.resolve(args.html);
  const outDir = path.resolve(args.outDir);
  if (!fs.existsSync(htmlPath) || !fs.statSync(htmlPath).isFile()) {
    throw new Error(`HTML 不存在：${htmlPath}`);
  }
  fs.mkdirSync(outDir, { recursive: true });

  const { chromium } = loadPlaywright();
  const chromePath =
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  const launchOptions = fs.existsSync(chromePath)
    ? { headless: true, executablePath: chromePath }
    : { headless: true, channel: "chrome" };

  const browser = await chromium.launch(launchOptions);
  const page = await browser.newPage({
    viewport: { width: 1200, height: 1500 },
    deviceScaleFactor: args.scale,
  });

  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts?.ready);
  await page.waitForTimeout(200);

  const sheets = page.locator(args.selector);
  const count = await sheets.count();
  const allProblems = [];
  if (count < args.minPages) {
    allProblems.push(`整组只有 ${count} 张，少于要求的 ${args.minPages} 张`);
  }

  if (args.guides) {
    await page.addStyleTag({ content: GUIDE_CSS });
    await sheets.evaluateAll((nodes) =>
      nodes.forEach((node) => {
        const guide = document.createElement("div");
        guide.className = "__xhs_guides__";
        node.appendChild(guide);
      }),
    );
  }

  for (let index = 0; index < count; index += 1) {
    const sheet = sheets.nth(index);
    const problems = await sheet.evaluate(checkSheet);
    const outPath = path.join(
      outDir,
      `${String(index + 1).padStart(2, "0")}.png`,
    );
    await sheet.screenshot({ path: outPath, type: "png" });
    if (problems.length) {
      console.log(`⚠ ${outPath}`);
      for (const problem of problems) {
        console.log(`  - ${problem}`);
        allProblems.push(`第 ${index + 1} 张：${problem}`);
      }
    } else {
      console.log(`✓ ${outPath}`);
    }
  }

  await browser.close();
  console.log(
    `完成 ${count} 张检查图，输出尺寸 ${Math.round(WIDTH * args.scale)}×${Math.round(HEIGHT * args.scale)}`,
  );

  if (allProblems.length) {
    console.log(`共发现 ${allProblems.length} 个问题：`);
    allProblems.forEach((problem) => console.log(`- ${problem}`));
    if (args.strict) process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error.message || error);
  process.exitCode = 1;
});
