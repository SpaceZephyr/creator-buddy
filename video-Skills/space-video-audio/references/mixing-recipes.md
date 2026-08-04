# 混音 ffmpeg 配方

`scripts/mix.sh` 是封装版，这里是底层配方，特殊需求时手改。

## 目标响度

- 成片整体：**-14 LUFS**（YouTube/多数平台参考值），真峰 -1 dB
- 人声(前景)：先 -16 LUFS 归一，再进混音
- BGM 垫底：无人声 -12~-16 dB；有人声 -20~-26 dB

## 1. BGM 循环 + 裁切到视频长度

```bash
# -stream_loop -1 无限循环，-t 裁到 DUR
ffmpeg -stream_loop -1 -i bgm.mp3 -t $DUR -c:a pcm_s16le bgm_fit.wav
```

## 2. 淡入淡出

```
afade=t=in:st=0:d=1.0, afade=t=out:st=$(DUR-1.0):d=1.0
```

## 3. 压音 ducking（人声一响 BGM 下沉）

```
[bgm][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[bgducked]
```
- `threshold` 越低越容易触发下沉；`ratio` 越大压得越狠
- `release` 300ms：人声停多久后 BGM 回来，太短会「抽气」
- 注意：sidechain 的 key 是**人声**，被压的是 **BGM**

## 4. 合并

```
[voice][bgducked]amix=inputs=2:normalize=0
```
`normalize=0` 关键——否则 amix 会把两轨都压半、忽大忽小。

## 5. 纯 B-roll（无前景音）只铺 BGM

```bash
ffmpeg -i broll.mp4 -stream_loop -1 -i bgm.mp3 \
  -filter_complex "[1:a]afade=t=in:st=0:d=1,afade=t=out:st=$FOUT:d=1,volume=-14dB,loudnorm=I=-14:TP=-1[a]" \
  -map 0:v -map "[a]" -t $DUR -c:v copy -c:a aac -b:a 192k out.mp4
```

## 6. 只换/加音轨，不动画面

`-c:v copy` 全程保留，混音只重编码音频（aac 192k）。画质零损失、速度快。

## 常见坑

- amix 不加 `normalize=0` → 音量忽大忽小
- BGM 比视频短又没循环 → 后半段静音
- 没做 loudnorm → 换平台后忽大忽小
- ducking 的 sidechain 接反（被压的接成了人声）→ 人声被压没了
