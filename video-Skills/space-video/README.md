# space-video · 视频创作 Skill 矩阵

一套面向自媒体视频创作的 `space-` 技能矩阵，把一条视频从「参考 → 选题 → 脚本 → 剪辑 → B-roll → 字幕 → 封面」拆成单一职责、可单用也可串联的技能。

## 技能清单

| 技能 | 职责 |
|---|---|
| **space-video** | 总控/导演：判断走哪步、路由子技能、成片后复盘 |
| **space-video-topic** | 选题前端：下载去水印 · 逐字稿 · 选题/钩子 · 标题 · 正文 |
| **space-video-script** | 脚本：去 AI 味口播稿 + 精确到秒分镜 |
| **space-video-edit** | 剪辑：剪口播（删前保后 + 风险分层）+ 口播成片 |
| **space-video-broll** | B-roll：HTML→确定性 MP4 的动画/motion 画面（代码渲染） |
| **space-video-broll-sketch** | B-roll：文章转手绘图解，调视频模型(Seedance/libtv)逐帧生成 |
| **space-video-subtitle** | 字幕：转写 · 断句 · AI 校对 · SRT/ASS · 烧录 |
| **space-video-audio** | 配音配乐：TTS 旁白 · 找 BGM 下载 · 压音混音 · 响度归一 |
| **space-video-cover** | 封面：家族气质 + 平台比例 + 高点击缩略图 |

## 串联用法

```
说「从头帮我做一条视频」→ space-video 接管，逐环节调子技能，文件落盘交接
```

各技能也可单独触发，见每个 SKILL.md 的触发词。

---

## 致谢与引用来源

本矩阵在设计与方法论上参考、借鉴了以下开源项目，并对其能力做了简化、拆解与重组：

**Skill 架构与视频创作方法论**
- [Pluviobyte/rnskill](https://github.com/Pluviobyte/rnskill) — Skill 工作流串联模式、视频创作技能分类
- [chengfeng / AI产品自由 · chengfeng-videocut-skills](https://github.com/Agentchengfeng/chengfeng-videocut-skills)（收录于 rnskill）— 剪口播「删前保后」「删除风险分层」方法论、口播成片分镜/时间轴流程，是 `space-video-edit` 的主要参考

**视频下载与文案提取**
- [yzfly/douyin-mcp-server](https://github.com/yzfly/douyin-mcp-server) — 抖音无水印下载、SenseVoice 语音转文案思路，参考进 `space-video-topic` / `space-video-subtitle`

**配音 / TTS**
- rnskill `tts-skill`（IndexTTS2 本地克隆音色路由方法论）— 参考进 `space-video-audio` 的 TTS 分档策略

**脚本/分镜规格**
- [feicaiclub/video-spec-builder](https://github.com/feicaiclub/video-spec-builder) — 「把模糊想法逼成精确到秒的分镜脚本」理念，参考进 `space-video-script`

**B-roll 渲染**
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) — HTML→确定性 MP4、可寻址动画机制，是 `space-video-broll` 的技术路线基础

**视频模型（生成式 B-roll）**
- 火山引擎 **Seedance 2.0**（火山方舟 Ark API，`doubao-seedance-2-0-*`）— `space-video-broll-sketch` 的 Seedance 通道
- **libtv Agent**（复用本地 `libtv-skill` 的 agent-im OpenAPI）— `space-video-broll-sketch` 的 libtv 通道

**编排复用的本地技能**（矩阵不重复造轮子，直接路由）
- 去 AI 味：`Humanizer-zh`｜口播转换：`podcast-script-generator`
- B-roll 渲染：`hyperframes` / `hyperframes-cli` / `hyperframes-media` / `remotion-video`
- 动画适配器：`gsap` / `animejs` / `css-animations` / `waapi` / `three` / `lottie`
- 标题：`baokuan-title-generator`｜选题：`topic-generator` / `topic-collector`
- 逐字稿：`youtube-transcript-cn` / `content-digest`
- 封面出图：`image-studio` / `space-article-cover-and-batch-illustration`

各来源的版权与许可归原作者所有。
