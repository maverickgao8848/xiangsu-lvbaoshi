(function () {
  'use strict';
  const { esc, check } = window.GLBase;
  const modules = window.GLSampleModules;
  const title = (data, fallback) => esc(data.title || fallback);
  const reveal = (ctx, selector, at = 0.2, from = {}, to = {}) => {
    ctx.tl.fromTo(ctx.q(selector), { opacity: 0, y: 28, ...from }, {
      opacity: 1, y: 0, duration: 0.65, ease: 'power3.out', ...to
    }, at);
  };
  const leave = (ctx, selector, at = 5.25) => {
    if(ctx.signature&&at>=5)return;
    ctx.tl.fromTo(ctx.q(selector), { opacity: 1 }, {
      opacity: 0, duration: 0.55, ease: 'power2.in', immediateRender: false
    }, at);
  };
  const draw = (ctx, selector, at, duration = 0.45) => {
    ctx.q(selector).forEach(path => {
      const length = path.getTotalLength();
      path.style.strokeDasharray = String(length);
      ctx.tl.fromTo(path, { strokeDashoffset: length }, {
        strokeDashoffset: 0, duration, ease: 'power2.out'
      }, at);
    });
  };

  modules.L10 = {
    render(data) {
      return `<div class="v-flow v-l10">
        <div class="v-ratio-heading">${title(data, '分工的两种重量')}</div>
        <div class="v-ratio-plane v-ratio-tool"><div class="v-ratio-value lime">80<span>%</span></div><div class="v-ratio-label">工具</div><div class="v-ratio-note muted">示例比例</div></div>
        <div class="v-ratio-plane v-ratio-judgment"><div class="v-ratio-value lime">20<span>%</span></div><div class="v-ratio-label">判断</div></div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-ratio-heading', 0.12, { x: -25 }, { x: 0 });
      reveal(ctx, '.v-ratio-tool', 0.25, { x: -80, y: -35, rotationY: 19, rotationZ: -12 }, { x: 0, y: 0, rotationY: 10, rotationZ: -7, duration: 0.9 });
      reveal(ctx, '.v-ratio-judgment', 0.78, { x: 100, y: 55, rotationY: -21, rotationZ: 13 }, { x: 0, y: 0, rotationY: -12, rotationZ: 8, duration: 0.95 });
      leave(ctx, '.v-l10');
    }
  };

  modules.L11 = {
    render(data) {
      return `<div class="v-flow v-l11">
        <div class="v-trade-heading">${title(data, '先确定取舍的基准')}</div>
        <div class="v-trade-option v-trade-left"><div class="kicker">选择 A</div><div class="v-trade-word">信息更全</div><div class="v-trade-detail muted">多保留一层细节</div></div>
        <div class="v-trade-option v-trade-right"><div class="kicker">选择 B</div><div class="v-trade-word">重点更清</div><div class="v-trade-detail muted">少一点阅读负担</div></div>
        <svg class="v-trade-link" viewBox="0 0 1920 1080" aria-hidden="true"><path d="M385 530V680H690M1535 530V680H1230"/></svg>
        <div class="v-trade-basis"><span class="v-trade-basis-label muted">共同判断基准</span><span class="v-trade-basis-value lime">观众能否一眼抓住主句</span></div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-trade-heading', 0.1);
      reveal(ctx, '.v-trade-basis', 0.35, { y: 45 }, { duration: 0.75 });
      reveal(ctx, '.v-trade-left', 1.0, { x: -45 }, { x: 0 });
      reveal(ctx, '.v-trade-right', 1.3, { x: 45 }, { x: 0 });
      draw(ctx, '.v-trade-link path', 1.72, 0.65);
      ctx.tl.fromTo(ctx.q('.v-trade-basis-value'), { color: '#f5f6f2' }, { color: '#d7ff48', duration: 0.4 }, 2.45);
      leave(ctx, '.v-l11');
    }
  };

  modules.L12 = {
    render(data) {
      return `<div class="v-flow v-l12">
        <div class="v-verdict-heading">${title(data, '哪个方案服务这句话？')}</div>
        <div class="v-verdict-stage">
          <div class="v-verdict-card v-verdict-a"><div class="kicker">方案 A</div><div class="v-verdict-word">堆满特效</div><div class="v-verdict-detail muted">每一层都抢注意力</div><div class="v-verdict-scratch"><span></span><span></span><span></span></div></div>
          <div class="v-verdict-card v-verdict-b"><div class="kicker">方案 B</div><div class="v-verdict-word">突出重点</div><div class="v-verdict-detail muted">让视觉替主句让路</div><div class="v-verdict-mark">${check}</div></div>
        </div>
        <div class="v-verdict-result"><span class="muted">本次选择</span><strong>突出重点</strong></div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-verdict-heading', 0.12);
      reveal(ctx, '.v-verdict-a', 0.25, { x: -240, rotationY: 27, rotationZ: -5 }, { x: 0, rotationY: 13, rotationZ: -3, duration: 0.85 });
      reveal(ctx, '.v-verdict-b', 0.38, { x: 240, rotationY: -27, rotationZ: 5 }, { x: 0, rotationY: -13, rotationZ: 3, duration: 0.85 });
      ctx.tl.fromTo(ctx.q('.v-verdict-a'), { opacity: 1 }, { opacity: 0.4, duration: 0.45, immediateRender: false }, 2.8);
      ctx.tl.fromTo(ctx.q('.v-verdict-b'), { backgroundColor: '#111619', borderColor: '#617074' }, { backgroundColor: '#d7ff48', borderColor: '#d7ff48', duration: 0.45 }, 2.8);
      ctx.tl.fromTo(ctx.q('.v-verdict-b .kicker, .v-verdict-b .v-verdict-word, .v-verdict-b .v-verdict-detail'), { color: '#f5f6f2' }, { color: '#17200e', duration: 0.45 }, 2.8);
      draw(ctx, '.v-verdict-mark path', 3.05, 0.5);
      reveal(ctx, '.v-verdict-result', 3.45, { y: 15 }, { duration: 0.5 });
      leave(ctx, '.v-l12', 5.35);
    }
  };

  modules.L13 = {
    render(data, A) {
      const source = esc(A + 'host.jpg');
      return `<div class="v-flow v-l13">
        <div class="v-compare-heading">${title(data, '同尺度，换一种说明结构')}</div>
        <div class="v-compare-media">
          <img class="v-compare-photo" src="${source}" alt="同一演示素材"/>
          <div class="v-compare-old"><div class="v-compare-label">原说明</div><div class="v-compare-old-copy"><span>素材就绪</span><span>步骤完成</span><span>重点确认</span></div></div>
          <div class="v-compare-reveal"><img class="v-compare-photo" src="${source}" alt="同一演示素材，尺度保持一致"/><div class="v-compare-new"><div class="v-compare-label">新说明</div><strong>先看重点</strong><span>素材与步骤，随后补充</span></div></div>
          <div class="v-compare-divider"><span>↔</span></div>
        </div>
        <div class="v-compare-note muted">两侧使用同一图片、同一尺度；本例仅比较说明的阅读结构。</div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-compare-heading', 0.12);
      reveal(ctx, '.v-compare-media', 0.28, { y: 24 }, { duration: 0.75 });
      const media = ctx.q('.v-compare-media')[0];
      const width = media.getBoundingClientRect().width;
      ctx.tl.fromTo(ctx.q('.v-compare-reveal'), { clipPath: 'inset(0% 0% 0% 100%)' }, { clipPath: 'inset(0% 0% 0% 50%)', duration: 1.55, ease: 'power2.inOut' }, 1.2);
      ctx.tl.fromTo(ctx.q('.v-compare-divider'), { x: width, opacity: 0 }, { x: width * 0.5, opacity: 1, duration: 1.55, ease: 'power2.inOut' }, 1.2);
      reveal(ctx, '.v-compare-note', 2.45, { y: 10 }, { duration: 0.5 });
      leave(ctx, '.v-l13', 5.35);
    }
  };

  modules.L14 = {
    render(data) {
      return `<div class="v-flow v-l14"><div class="v-checklist">
        <div class="v-checklist-heading">${title(data, '完成清单')}</div>
        ${['素材就绪', '重点确认', '节奏完成'].map((word, i) => `<div class="v-checklist-row v-checklist-row-${i}"><span class="v-checklist-order">0${i + 1}</span><strong>${word}</strong><span class="v-checklist-tick lime">${check}</span></div>`).join('')}
      </div></div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-checklist', 0.15, { x: -100, rotationY: 14, rotationZ: -12 }, { x: 0, rotationY: 8, rotationZ: -7, duration: 0.95 });
      reveal(ctx, '.v-checklist-heading', 0.18, { y: -15 });
      [0, 1, 2].forEach(i => {
        reveal(ctx, `.v-checklist-row-${i} strong, .v-checklist-row-${i} .v-checklist-order`, 0.55 + i * 0.65, { x: -22, y: 0 }, { x: 0, duration: 0.45 });
        draw(ctx, `.v-checklist-row-${i} path`, 1.45 + i * 0.95, 0.48);
      });
      leave(ctx, '.v-l14');
    }
  };

  modules.L15 = {
    render(data) {
      return `<div class="v-flow v-l15">
        <div class="v-rail-heading">${title(data, '让步骤沿方向到站')}</div>
        <div class="v-rail-description muted">准备好，再核对，最后展示。</div>
        <svg class="v-rail-lines" viewBox="0 0 1920 1080" aria-hidden="true"><path class="v-rail-base" d="M328 525H1600"/><path class="v-rail-progress v-rail-segment-1" d="M328 525H960"/><path class="v-rail-progress v-rail-segment-2" d="M960 525H1600"/><path class="v-rail-arrow" d="M689 510L709 525L689 540M1326 510L1346 525L1326 540"/></svg>
        ${['先准备', '再核对', '再展示'].map((word, i) => `<div class="v-rail-station v-rail-station-${i}" style="left:${[270, 902, 1542][i]}px"><div class="v-rail-node"><span>0${i + 1}</span></div><strong>${word}</strong><div class="muted">${['素材进入', '确认关系', '交付表达'][i]}</div></div>`).join('')}
        <div class="v-rail-token"></div><div class="v-rail-end lime">完成一次信息交接</div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-rail-heading', 0.12);
      reveal(ctx, '.v-rail-description', 0.32, { y: 10 });
      reveal(ctx, '.v-rail-lines', 0.5, { y: 0 });
      reveal(ctx, '.v-rail-station', 0.52, { y: 25 }, { stagger: 0.16, duration: 0.55 });
      ctx.tl.fromTo(ctx.q('.v-rail-token'), { x: 328, scale: 0, opacity: 0 }, { x: 328, scale: 1, opacity: 1, duration: 0.35, ease: 'power2.out' }, 1.1);
      ctx.tl.fromTo(ctx.q('.v-rail-token'), { x: 328 }, { x: 960, duration: 0.85, ease: 'power2.inOut', immediateRender: false }, 1.75);
      draw(ctx, '.v-rail-segment-1', 1.75, 0.85);
      ctx.tl.fromTo(ctx.q('.v-rail-token'), { x: 960 }, { x: 1600, duration: 0.85, ease: 'power2.inOut', immediateRender: false }, 3.0);
      draw(ctx, '.v-rail-segment-2', 3.0, 0.85);
      [1.12, 2.6, 3.85].forEach((at, i) => ctx.tl.fromTo(ctx.q(`.v-rail-station-${i} .v-rail-node`), { borderColor: '#617074', color: '#f5f6f2' }, { borderColor: '#d7ff48', color: '#d7ff48', duration: 0.3 }, at));
      reveal(ctx, '.v-rail-end', 4.02, { y: 12 }, { duration: 0.45 });
      leave(ctx, '.v-l15', 5.35);
    }
  };

  modules.L16 = {
    render(data) {
      return `<div class="v-flow v-l16">
        <div class="v-orbit-heading">${title(data, '关键词环')}</div>
        <div class="v-orbit">
          <svg class="v-orbit-arrows" viewBox="0 0 600 600" aria-hidden="true"><circle cx="300" cy="300" r="202"/><path class="v-orbit-arrow v-orbit-arrow-0" d="M388 118A202 202 0 0 1 494 350M479 334L494 350L510 335"/><path class="v-orbit-arrow v-orbit-arrow-1" d="M447 438A202 202 0 0 1 147 433M169 432L147 433L148 455"/><path class="v-orbit-arrow v-orbit-arrow-2" d="M103 330A202 202 0 0 1 218 113M198 111L218 113L216 135"/></svg>
          <div class="v-orbit-word v-orbit-word-0">先准备</div><div class="v-orbit-word v-orbit-word-1">再核对</div><div class="v-orbit-word v-orbit-word-2">再展示</div><div class="v-orbit-center"><span class="muted">当前阶段</span><strong class="v-orbit-center-0">准备</strong><strong class="v-orbit-center-1">核对</strong><strong class="v-orbit-center-2">展示</strong></div>
        </div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-orbit-heading', 0.1, { x: -18 }, { x: 0 });
      reveal(ctx, '.v-orbit', 0.23, { scale: 0.88, rotationZ: -10 }, { scale: 1, rotationZ: 0, duration: 0.9 });
      ctx.tl.fromTo(ctx.q('.v-orbit-word-0'), { rotationZ: 0 }, { rotationZ: 0, duration: 0.01 }, 0);
      ctx.tl.fromTo(ctx.q('.v-orbit-word-1'), { rotationZ: -60 }, { rotationZ: -60, duration: 0.01 }, 0);
      ctx.tl.fromTo(ctx.q('.v-orbit-word-2'), { rotationZ: 60 }, { rotationZ: 60, duration: 0.01 }, 0);
      [0.75, 2.05, 3.4].forEach((at, i) => {
        ctx.tl.fromTo(ctx.q(`.v-orbit-word-${i}, .v-orbit-arrow-${i}`), { color: '#a8afb4' }, { color: '#d7ff48', duration: 0.25 }, at);
        reveal(ctx, `.v-orbit-center-${i}`, at, { y: 8 }, { duration: 0.25 });
        if (i < 2) {
          ctx.tl.fromTo(ctx.q(`.v-orbit-word-${i}, .v-orbit-arrow-${i}`), { color: '#d7ff48' }, { color: '#a8afb4', duration: 0.25, immediateRender: false }, at + 1.05);
          leave(ctx, `.v-orbit-center-${i}`, at + 1.03);
        }
      });
      leave(ctx, '.v-l16');
    }
  };

  modules.L17 = {
    render(data) {
      return `<div class="v-flow v-l17">
        <div class="v-quote-source">出处 · 示例原文《样本文案》 · 第 2 段</div>
        <div class="v-quote-glyph lime">“</div>
        <div class="v-quote-copy"><div class="v-quote-first">${title(data, '让重点先被看见，')}</div><div class="v-quote-key"><span class="v-quote-highlight"></span><strong>让细节随后抵达。</strong></div></div>
        <svg class="v-quote-underline" viewBox="0 0 1920 1080" aria-hidden="true"><path d="M345 681H1490"/></svg>
        <div class="v-quote-citation muted">示例原文：《样本文案》“阅读顺序”，第 2 段；本轮自编，用于摘句效果演示。</div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-quote-source', 0.12, { y: 12 });
      reveal(ctx, '.v-quote-glyph', 0.65, { y: -30, scale: 0.85 }, { scale: 1, duration: 0.55 });
      reveal(ctx, '.v-quote-first', 1.0, { x: -30, y: 0 }, { x: 0, duration: 0.65 });
      reveal(ctx, '.v-quote-key strong', 1.45, { x: -30, y: 0 }, { x: 0, duration: 0.65 });
      ctx.tl.fromTo(ctx.q('.v-quote-highlight'), { scaleX: 0 }, { scaleX: 1, duration: 0.65, ease: 'power2.inOut' }, 2.4);
      ctx.tl.fromTo(ctx.q('.v-quote-key strong'), { color: '#f5f6f2' }, { color: '#17200e', duration: 0.4, immediateRender: false }, 2.55);
      draw(ctx, '.v-quote-underline path', 2.58, 0.7);
      reveal(ctx, '.v-quote-citation', 3.2, { y: 8 }, { duration: 0.4 });
      leave(ctx, '.v-l17', 5.35);
    }
  };

  modules.L18 = {
    render(data) {
      return `<div class="v-flow v-l18">
        <div class="v-doc-heading">${title(data, '保留上下文，再标出重点')}</div>
        <div class="v-doc-page"><div class="v-doc-name">样本编辑说明 <span class="muted">/ 阅读顺序</span></div>
          <div class="v-doc-line v-doc-line-1"><span class="v-doc-number muted">01</span><span>画面中的每一层，都应承担明确的阅读任务。</span></div>
          <div class="v-doc-line v-doc-line-2"><span class="v-doc-highlight"></span><span class="v-doc-number muted">02</span><strong>先让观众理解重点，再安排细节逐步进入。</strong></div>
          <div class="v-doc-line v-doc-line-3"><span class="v-doc-number muted">03</span><span>保留必要上下文，避免摘句改变原本的意思。</span></div>
        </div>
        <div class="v-doc-source muted">来源：示例文档《样本编辑说明》，第 2 节“阅读顺序”，第 1–3 段（本轮自编）。</div>
      </div>`;
    },
    motion(ctx) {
      reveal(ctx, '.v-doc-heading', 0.12);
      reveal(ctx, '.v-doc-page', 0.38, { y: 40 }, { duration: 0.8 });
      reveal(ctx, '.v-doc-name', 0.6, { y: 8 });
      reveal(ctx, '.v-doc-line', 0.85, { x: -20, y: 0 }, { x: 0, duration: 0.5, stagger: 0.18 });
      ctx.tl.fromTo(ctx.q('.v-doc-highlight'), { scaleX: 0 }, { scaleX: 1, duration: 0.85, ease: 'power2.inOut' }, 2.0);
      ctx.tl.fromTo(ctx.q('.v-doc-line-2 strong, .v-doc-line-2 .v-doc-number'), { color: '#f5f6f2' }, { color: '#17200e', duration: 0.45, immediateRender: false }, 2.23);
      reveal(ctx, '.v-doc-source', 2.85, { y: 8 }, { duration: 0.4 });
      leave(ctx, '.v-l18', 5.35);
    }
  };
}());
