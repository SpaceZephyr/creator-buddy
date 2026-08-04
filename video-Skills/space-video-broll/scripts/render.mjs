// 确定性 B-roll 渲染器：HTML(seek 驱动) → 逐帧截图 → ffmpeg → MP4
// 用法: node render.mjs <html> <out.mp4> [fps=30]
// HTML 约定: 暴露 window.DURATION(秒) 和 window.seek(t)（把画面置于第 t 秒的状态）
import puppeteer from "puppeteer-core";
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, existsSync } from "node:fs";
import path from "node:path";

const [htmlArg, outArg, fpsArg] = process.argv.slice(2);
const fps = Number(fpsArg || 30);
const html = path.resolve(htmlArg);
const out = path.resolve(outArg);
const W = 720, H = 896, SCALE = 2;

// 自动探测缓存的 chrome-headless-shell（puppeteer 下载的）
import { globSync } from "node:fs";
const CHROME = process.env.CHROME_PATH
  || globSync(process.env.HOME + "/.cache/puppeteer/chrome-headless-shell/*/*/chrome-headless-shell")[0]
  || globSync(process.env.HOME + "/.cache/puppeteer/chrome/*/*/*/Contents/MacOS/Google Chrome for Testing")[0];
if (!CHROME) { console.error("找不到缓存的 chrome，设 CHROME_PATH 环境变量指定"); process.exit(1); }
const framesDir = path.resolve("frames");
if (existsSync(framesDir)) rmSync(framesDir, { recursive: true });
mkdirSync(framesDir, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ["--no-sandbox", "--force-color-profile=srgb", "--hide-scrollbars"],
});
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: SCALE });
await page.goto("file://" + html, { waitUntil: "networkidle0" });
// 等字体就绪，确定性
await page.evaluate(async () => { if (document.fonts) await document.fonts.ready; });

const duration = await page.evaluate(() => window.DURATION || 3);
const total = Math.round(duration * fps);
process.stdout.write(`渲染 ${htmlArg}  ${duration}s @${fps}fps = ${total} 帧\n`);

for (let i = 0; i < total; i++) {
  const t = i / fps;
  await page.evaluate((t) => window.seek(t), t);
  const f = path.join(framesDir, `f_${String(i).padStart(5, "0")}.png`);
  await page.screenshot({ path: f });
  if (i % 15 === 0) process.stdout.write(`  ${i}/${total}\r`);
}
await browser.close();

// 逐帧 → MP4（缩回 720x896，yuv420p 通用兼容）
execFileSync("ffmpeg", [
  "-y", "-framerate", String(fps),
  "-i", path.join(framesDir, "f_%05d.png"),
  "-vf", `scale=${W}:${H}:flags=lanczos`,
  "-c:v", "libx264", "-preset", "slow", "-crf", "18",
  "-pix_fmt", "yuv420p", out,
], { stdio: "inherit" });

rmSync(framesDir, { recursive: true });
console.log("\n✅ " + out);
