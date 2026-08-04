#!/usr/bin/env python3
"""火山引擎 Seedance 2.0 视频生成（Ark 异步任务）。仅用标准库。

一次性：建任务 → 轮询 → 下载 MP4。

用法：
  export ARK_API_KEY=xxx
  # 文生视频
  python3 seedance.py --prompt "白底手绘线稿逐笔画出，元素依次生长" \
      --ratio 4:3 --duration 5 --resolution 720p --out clip.mp4
  # 图生视频（首帧）：--image 可为本地路径或 URL
  python3 seedance.py --prompt "手绘生长动效，镜头静止" \
      --image frame01.png --ratio 4:3 --duration 5 --out clip.mp4

环境变量：
  ARK_API_KEY          必填
  ARK_BASE             可选，默认 https://ark.cn-beijing.volces.com/api/v3
  ARK_SEEDANCE_MODEL   可选，默认 doubao-seedance-2-0-260128
"""
import argparse, base64, json, mimetypes, os, sys, time, urllib.request, urllib.error

BASE = os.environ.get("ARK_BASE", "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")
MODEL = os.environ.get("ARK_SEEDANCE_MODEL", "doubao-seedance-2-0-260128")
KEY = os.environ.get("ARK_API_KEY")


def _req(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + (KEY or ""))
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit("HTTP %s: %s" % (e.code, e.read().decode()[:500]))


def _image_field(image):
    """本地路径 → base64 data URL；URL 原样。"""
    if image.startswith("http://") or image.startswith("https://"):
        return image
    mime = mimetypes.guess_type(image)[0] or "image/png"
    with open(image, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return "data:%s;base64,%s" % (mime, b64)


def create_task(prompt, image, ratio, duration, resolution, watermark):
    # Seedance 用文本内联参数控制画幅/时长/分辨率
    text = "%s --ratio %s --dur %s --rs %s --wm %s" % (
        prompt, ratio, duration, resolution, "true" if watermark else "false")
    content = [{"type": "text", "text": text}]
    if image:
        content.append({"type": "image_url",
                        "image_url": {"url": _image_field(image)},
                        "role": "first_frame"})
    out = _req("POST", BASE + "/contents/generations/tasks",
               {"model": MODEL, "content": content})
    tid = out.get("id") or out.get("task_id")
    if not tid:
        sys.exit("未拿到任务 id：" + json.dumps(out)[:400])
    return tid


def poll(tid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        out = _req("GET", BASE + "/contents/generations/tasks/" + tid)
        st = out.get("status", "")
        if st in ("succeeded", "success"):
            c = out.get("content") or {}
            url = c.get("video_url") or out.get("video_url")
            if not url:
                sys.exit("成功但无 video_url：" + json.dumps(out)[:400])
            return url
        if st in ("failed", "error", "cancelled"):
            sys.exit("任务失败：" + json.dumps(out)[:400])
        print("  ...%s (%ds)" % (st or "pending", int(time.time() - t0)))
        time.sleep(5)
    sys.exit("轮询超时")


def download(url, out):
    urllib.request.urlretrieve(url, out)
    print("✅ %s" % out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--image", help="首帧图：本地路径或 URL")
    ap.add_argument("--ratio", default="4:3")
    ap.add_argument("--duration", default="5")
    ap.add_argument("--resolution", default="720p", choices=["480p", "720p", "1080p"])
    ap.add_argument("--watermark", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not KEY:
        sys.exit("缺 ARK_API_KEY 环境变量")
    print("模型 %s | %s | %ss | %s" % (MODEL, a.ratio, a.duration, a.resolution))
    tid = create_task(a.prompt, a.image, a.ratio, a.duration, a.resolution, a.watermark)
    print("任务 %s，轮询中…" % tid)
    url = poll(tid)
    download(url, a.out)


if __name__ == "__main__":
    main()
