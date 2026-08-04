#!/usr/bin/env python3
"""
Chart Image Generator - 使用 LabNana GPT-image-2 生成图表图片

Usage:
    python3 generate_chart.py --type flowchart --content "..." --output /path/to/output.png

Env:
    LABNANA_API_KEY - LabNana API key (自动从 .labnana.env 读取)
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

# LabNana 配置
LABNANA_API_URL = "https://api.labnana.com"
LABNANA_MODEL = "gpt-image-2"
LABNANA_PROVIDER = "openai"

DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_RESOLUTION = "2K"
MAX_RETRIES = 3
RETRY_DELAY = 5

# 图表类型映射
CHART_TYPES = {
    "flowchart": "流程图",
    "architecture": "架构图",
    "er": "ER图",
    "bmc": "商业模式画布",
    "journey": "用户旅程图",
    "mindmap": "思维导图",
    "competitive": "竞品分析图",
    "swot": "SWOT分析",
    "roadmap": "产品路线图",
    "orgchart": "组织架构图",
}

# 视觉风格
STYLE_CHOICES = [
    "blueprint",
    "notion",
    "sketch-notes",
    "corporate",
    "dark-atmospheric",
    "watercolor",
]

# 风格前缀库
STYLE_PREFIXES = {
    "blueprint": (
        "A precise technical blueprint-style {chart_type} diagram.\n"
        "Background: Off-white (#FAF8F5) with subtle grid lines.\n"
        "Colors: Engineering Blue (#2563EB), Deep Slate (#334155), Navy (#1E3A5F), Light Blue (#BFDBFE).\n"
        "Line art with clean geometric shapes, dimension lines, precise connections.\n"
        "Thin borders, subtle shadows for depth. Professional engineering drawing feel.\n\n"
        "ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).\n"
        "Use clean sans-serif Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.\n"
        "No photography, no realistic elements, no complex gradients, no 3D effects."
    ),
    "notion": (
        "A clean minimal {chart_type} diagram in Notion style.\n"
        "Background: Pure white (#FFFFFF) with subtle dot grid.\n"
        "Colors: Dark text (#37352f), subtle borders (#E3E2E0), accent blue (#2383E2), light fills (#F7F7F5).\n"
        "Clean rectangular shapes with rounded corners, thin 1px borders.\n"
        "Generous whitespace, geometric alignment, information-dense but organized.\n\n"
        "ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).\n"
        "Use clean sans-serif Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.\n"
        "No photography, no realistic elements, no complex gradients, no 3D effects."
    ),
    "sketch-notes": (
        "A hand-drawn sketch-notes style {chart_type} diagram.\n"
        "Background: Warm off-white (#FFF8F0) with subtle paper texture.\n"
        "Colors: Warm tones - terracotta (#C0562F), forest green (#2F7A5C), navy pen (#2D3748), amber highlight (#F6AD55).\n"
        "Marker-style thick outlines, slightly wobbly organic lines.\n"
        "Handwritten feel, doodle-style icons, sticky-note shapes, arrow doodles.\n\n"
        "ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).\n"
        "Use friendly rounded Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.\n"
        "No photography, no realistic elements, no complex gradients, no 3D effects."
    ),
    "corporate": (
        "A professional corporate-style {chart_type} diagram.\n"
        "Background: White (#FFFFFF) with navy (#1E3A5F) header band and subtle pinstripe accents.\n"
        "Colors: Navy (#1E3A5F), Gold (#C5A55A), Charcoal (#4A4A4A), Silver (#B0B0B0), Light Gray (#F5F5F5).\n"
        "Sharp geometric shapes, gold accent lines, clean serif typography.\n"
        "Executive dashboard feel, data-driven, investment-grade presentation.\n\n"
        "ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).\n"
        "Use professional Chinese font (serif for titles). Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.\n"
        "No photography, no realistic elements, no complex gradients, no 3D effects."
    ),
    "dark-atmospheric": (
        "A dark atmospheric {chart_type} diagram with glowing neon elements.\n"
        "Background: Deep dark (#0A0A0B) with subtle grid overlay.\n"
        "Colors: Neon cyan (#00F5FF), electric purple (#A855F7), hot pink (#F472B6), amber glow (#FBBF24).\n"
        "Glowing connection lines, luminous node borders, gradient light effects on edges.\n"
        "Futuristic dashboard feel, cyberpunk-inspired, high-tech aesthetic.\n\n"
        "ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).\n"
        "Use clean light-colored Chinese font on dark background. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.\n"
        "No photography, no realistic elements, no complex gradients on flat surfaces, no 3D effects."
    ),
    "watercolor": (
        "A soft watercolor-style {chart_type} diagram.\n"
        "Background: Warm cream (#FEFCF8) with subtle watercolor wash texture.\n"
        "Colors: Soft pastels - rose pink (#FBBFCA), sky blue (#A3D5FF), lavender (#C4B5FD), sage green (#A7F3D0), peach (#FED7AA).\n"
        "Watercolor paint fill for shapes, soft bleeding edges, gentle color transitions.\n"
        "Organic flowing connections, hand-painted feel, warm and approachable.\n\n"
        "ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).\n"
        "Use rounded friendly Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.\n"
        "No photography, no realistic elements, no sharp geometric shapes, no 3D effects."
    ),
}


def _save_image_from_base64(base64_data, output_path):
    """Save base64 image data to file."""
    img_data = base64.b64decode(base64_data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_data)
    return len(img_data)


def _do_http_request(endpoint, payload, headers, timeout=120):
    """Execute HTTP request with retry logic."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            error = {"code": e.code, "message": body[:500]}
            if e.code == 429 or e.code >= 500:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_DELAY * (attempt + 1)
                    print(f"[INFO] 限流或服务器错误，{wait}秒后重试...", file=sys.stderr)
                    time.sleep(wait)
                    continue
            return None, error
        except Exception as e:
            error = {"code": -1, "message": str(e)}
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None, error
    return None, {"code": -1, "message": "Max retries exceeded"}


def generate_chart(prompt, output_path, api_key, api_url=LABNANA_API_URL,
                   model=LABNANA_MODEL, provider=LABNANA_PROVIDER,
                   aspect_ratio=DEFAULT_ASPECT_RATIO, resolution=DEFAULT_RESOLUTION):
    """Call LabNana API to generate a chart image."""
    endpoint = f"{api_url}/openapi/v1/images/generation"

    payload = {
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "imageConfig": {
            "aspectRatio": aspect_ratio,
            "imageSize": resolution
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"[INFO] 正在调用 LabNana API 生成图表...", file=sys.stderr)
    result, error = _do_http_request(endpoint, payload, headers)

    if error:
        print(f"[ERROR] LabNana API 错误: {error}", file=sys.stderr)
        return None

    # Extract image from response
    candidates = result.get("candidates", [])
    if not candidates:
        print(f"[WARN] API 响应中没有图片数据", file=sys.stderr)
        return None

    content = candidates[0].get("content", {})
    parts = content.get("parts", [])

    for part in parts:
        if "inlineData" in part:
            inline = part["inlineData"]
            base64_data = inline.get("data", "")
            if base64_data:
                size = _save_image_from_base64(base64_data, output_path)
                print(f"[OK] 图表已保存: {output_path} ({size} bytes)", file=sys.stderr)
                return output_path

    print(f"[WARN] 响应中没有找到图片数据", file=sys.stderr)
    return None


def load_api_key():
    """Load API key from .labnana.env file."""
    # 首先检查环境变量
    env_key = os.environ.get("LABNANA_API_KEY")
    if env_key:
        return env_key

    # 然后尝试从 .labnana.env 文件读取
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(script_dir, "..", ".labnana.env")

    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("LABNANA_API_KEY="):
                    return line.strip().split("=", 1)[1]

    return None


def build_prompt(chart_type, content, style="blueprint"):
    """
    根据图表类型和内容构建提示词。

    Args:
        chart_type: 图表类型 (flowchart, architecture, er, bmc, journey, mindmap, competitive, swot, roadmap, orgchart)
        content: 图表内容描述
        style: 风格 (blueprint, notion, sketch-notes, corporate, dark-atmospheric, watercolor)
    """
    chart_name = CHART_TYPES.get(chart_type, chart_type)
    prefix = STYLE_PREFIXES.get(style, STYLE_PREFIXES["blueprint"])
    style_prefix = prefix.replace("{chart_type}", chart_name)

    return f"{style_prefix}\n\n{content}"


def main():
    parser = argparse.ArgumentParser(description="使用 GPT-image-2 生成图表图片")
    parser.add_argument("--type", "-t", required=True, choices=list(CHART_TYPES.keys()),
                        help=f"图表类型: {', '.join(CHART_TYPES.keys())}")
    parser.add_argument("--content", "-c", required=True, help="图表内容描述")
    parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    parser.add_argument("--api-key", help="LabNana API key (可选，默认从 .labanana.env 读取)")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO,
                        help="宽高比: 1:1, 16:9, 21:9 (默认: 16:9)")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                        help="分辨率: 1K, 2K, 4K (默认: 2K)")
    parser.add_argument("--style", default="blueprint", choices=STYLE_CHOICES,
                        help="视觉风格: blueprint (蓝图工程), notion (简约), sketch-notes (手绘笔记), corporate (商务正装), dark-atmospheric (深色霓虹), watercolor (水彩柔和)")
    args = parser.parse_args()

    # 获取 API key
    api_key = args.api_key
    if not api_key:
        api_key = load_api_key()
    if not api_key:
        print("[ERROR] 无法获取 LabNana API Key。请设置 LABNANA_API_KEY 环境变量或在 .labnana.env 中配置。", file=sys.stderr)
        sys.exit(1)

    # 构建提示词
    prompt = build_prompt(args.type, args.content, args.style)

    # 生成图片
    result = generate_chart(
        prompt=prompt,
        output_path=args.output,
        api_key=api_key,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution
    )

    if result:
        print(f"[OK] 完成: {result}", file=sys.stderr)
        sys.exit(0)
    else:
        print("[ERROR] 图表生成失败。", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
