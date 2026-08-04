/* 多场景确定性时间轴助手（seek 驱动，不依赖时钟）
   用法：
     const T = Timeline();
     T.scene('#s1', 0, 4, (lt, p) => { ... });   // 选择器/元素, 起始秒, 时长, 更新函数
     T.scene('#s2', 4, 5, (lt, p) => { ... });
     T.build();                 // 设置 window.DURATION
     window.seek = T.seek;      // 暴露给渲染器
   缓动/工具挂在 window：clamp seg lerp eoc eob eic eio typed
*/
window.clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
window.lerp = (a, b, p) => a + (b - a) * p;
window.seg = (t, s, d) => clamp((t - s) / d);                 // 局部进度 0..1
window.eoc = (x) => 1 - Math.pow(1 - x, 3);                   // easeOutCubic
window.eic = (x) => x * x * x;                                // easeInCubic
window.eio = (x) => x < .5 ? 4*x*x*x : 1 - Math.pow(-2*x+2,3)/2; // easeInOutCubic
window.eob = (x) => { const c = 2.70158; return 1 + c*Math.pow(x-1,3) + 1.70158*Math.pow(x-1,2); }; // back out
// 打字：返回应显示的字符数
window.typed = (full, lt, cps = 18) => full.slice(0, Math.round(clamp(lt * cps, 0, full.length)));

function Timeline() {
  const scenes = [];
  const api = {
    scene(sel, start, dur, update) {
      const el = typeof sel === 'string' ? document.querySelector(sel) : sel;
      scenes.push({ el, start, dur, update, end: start + dur });
      return api;
    },
    build() {
      window.DURATION = Math.max(...scenes.map(s => s.end), 0);
      return api;
    },
    seek(t) {
      for (const s of scenes) {
        const active = t >= s.start && t < s.end + 0.001;
        if (s.el) s.el.style.display = active ? '' : 'none';
        if (active) {
          const lt = t - s.start;
          s.update(lt, clamp(lt / s.dur), s.el);
        }
      }
    },
  };
  return api;
}
window.Timeline = Timeline;
