(function () {
  'use strict';
  const B = window.GLBase;
  const M = window.GLSampleModules;
  const title = (data, fallback) => String(data && data.title ? data.title : fallback);
  const copy = (data, key, fallback) => B.esc(data && data[key] ? data[key] : fallback);
  const fit = (text, large, medium, small) => text.length > 20 ? small : text.length > 12 ? medium : large;
  const layer = (cls, body) => `<div class="f-layer ${cls}">${body}</div>`;
  const heading = (text, cls, sizes = [60, 48, 38]) => `<div class="${cls}" style="font-size:${fit(text, ...sizes)}px">${B.esc(text)}</div>`;
  function tween(ctx, selector, from, to, at) {
    ctx.tl.fromTo(ctx.q(selector), from, to, at);
  }
  function exit(ctx, selector, at = 5.25, from = {}) {
    if(ctx.signature&&at>=5)return;
    tween(ctx, selector, { opacity: 1, x: 0, y: 0, ...from }, {
      opacity: 0, y: 20, duration: 0.45, ease: 'power2.in', immediateRender: false
    }, at);
  }
  function draw(ctx, selector, at, duration = 0.55) {
    ctx.q(selector).forEach((path, i) => {
      const length = path.getTotalLength();
      path.style.strokeDasharray = String(length);
      ctx.tl.fromTo(path, { strokeDashoffset: length }, {
        strokeDashoffset: 0, duration, ease: 'power2.out'
      }, at + i * duration * 0.72);
    });
  }

  M.L02 = {
    render(data) {
      const word = title(data, '认知负荷');
      const wordSize = fit(word, 78, 56, 40);
      const lensHeight = Math.max(217, 115 + Math.ceil(word.length * wordSize / 434) * wordSize * 1.2);
      return layer('f-definition-scene', `<div class="f-lexicon glass" style="height:${lensHeight + 300}px">
        <div class="f-definition" style="top:${lensHeight}px">
          <div class="f-definition-rule"></div>
          <div class="f-definition-label kicker">它指的是</div>
          <div class="f-definition-copy">${copy(data, 'definition', '理解一段信息时，需要付出的脑力。')}</div>
          <div class="f-definition-note muted">${copy(data, 'note', '先减负，再加一层视觉。')}</div>
        </div>
        <div class="f-lens" style="height:${lensHeight}px">
          <div class="f-lens-kicker kicker">把一个词，展开来看</div>
          ${heading(word, 'f-lens-word', [78, 56, 40])}
          <span class="f-lens-plus lime" aria-hidden="true">＋</span>
        </div>
      </div>`);
    },
    motion(ctx) {
      const lensHeight=ctx.q('.f-lens')[0].offsetHeight;
      const expandedHeight=lensHeight+ctx.q('.f-definition')[0].offsetHeight;
      tween(ctx, '.f-lexicon', { opacity: 0, x: -55, scale: 0.94 },
        { opacity: 1, x: 0, scale: 1, duration: 0.75, ease: 'power3.out' }, 0.1);
      tween(ctx, '.f-lexicon', { height:lensHeight },
        { height:expandedHeight, duration:0.7, ease:'power3.inOut' },1.2);
      tween(ctx, '.f-definition', { opacity: 0, y: 18 },
        { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }, 1.4);
      tween(ctx, '.f-lens-plus', { rotation: 0 },
        { rotation: 45, duration: 0.4, ease: 'power2.inOut' }, 1.28);
      tween(ctx, '.f-definition-copy, .f-definition-note', { opacity: 0, y: -12 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.15, ease: 'power1.out' }, 1.52);
      exit(ctx, '.f-lexicon');
    }
  };

  M.L03 = {
    render(data) {
      const corrected = title(data, '重点越清楚越好');
      return layer('f-correction-scene', `<div class="f-correction">
        <div class="f-correction-kicker kicker">换个判断标准</div>
        <div class="f-old-wrap">
          <div class="f-old-copy"><span>${copy(data, 'old', '特效越多越好')}</span></div>
          <svg class="f-correction-stroke" aria-hidden="true"></svg>
        </div>
        <div class="f-new-wrap">
          <div class="f-correction-arrow lime" aria-hidden="true">↓</div>
          ${heading(corrected, 'f-new-copy', [65, 52, 42])}
          <div class="f-new-note">${copy(data, 'note', '把注意力，留给这一个重点。')}</div>
        </div>
      </div>`);
    },
    motion(ctx) {
      // Measure each displayed line after fonts load. The stroke shares the text's
      // parent, so entrances and later seeks cannot skew their alignment.
      const oldCopy = ctx.q('.f-old-copy span')[0];
      const svg = ctx.q('.f-correction-stroke')[0];
      const wrap = ctx.q('.f-old-wrap')[0];
      const bounds = wrap.getBoundingClientRect();
      const range = document.createRange();
      range.selectNodeContents(oldCopy);
      const lines = Array.from(range.getClientRects()).filter(rect => rect.width > 0);
      const scaleX = bounds.width / wrap.offsetWidth;
      const scaleY = bounds.height / wrap.offsetHeight;
      svg.setAttribute('viewBox', `0 0 ${wrap.offsetWidth} ${wrap.offsetHeight}`);
      svg.innerHTML = lines.map(rect => {
        const x1 = (rect.left - bounds.left) / scaleX;
        const x2 = (rect.right - bounds.left) / scaleX;
        const y = (rect.top + rect.height * 0.52 - bounds.top) / scaleY;
        return `<path d="M${x1} ${y}H${x2}"/>`;
      }).join('');
      tween(ctx, '.f-correction-kicker, .f-old-wrap', { x: -48, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.55, stagger: 0.16, ease: 'power3.out' }, 0.1);
      draw(ctx, '.f-correction-stroke path', 1.78, 0.45);
      tween(ctx, '.f-old-copy', { opacity: 1 },
        { opacity: 0.38, duration: 0.35, ease: 'power1.out', immediateRender: false }, 2.1);
      tween(ctx, '.f-new-wrap', { y: 65, opacity: 0, scale: 0.92 },
        { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: 'power3.out' }, 2.25);
      exit(ctx, '.f-correction');
    }
  };

  M.L04 = {
    render(data) {
      const word = title(data, '信息层级');
      const wordSize = fit(word, 64, 49, 38);
      const targetHeight = Math.max(116, Math.ceil(word.length * wordSize / 404) * wordSize * 1.2 + 42);
      const frameHeight = targetHeight + 30;
      const lowerTop = 197 + targetHeight + 42;
      return layer('f-keyword-scene', `<div class="f-keywords">
        <div class="f-keyword-label kicker">现在只看一个词</div>
        <div class="f-key-back f-key-one">节奏</div>
        <div class="f-key-back f-key-two">材质</div>
        <div class="f-key-target glass" style="min-height:${targetHeight}px">${heading(word, 'f-key-target-copy', [64, 49, 38])}</div>
        <div class="f-key-back f-key-three" style="top:${lowerTop}px">画面</div>
        <div class="f-key-back f-key-four" style="top:${lowerTop}px">语气</div>
        <svg class="f-key-frame" style="height:${frameHeight}px" viewBox="0 0 505 ${frameHeight}" aria-hidden="true">
          <path d="M42 8L8 8L8 42M463 8L497 8L497 42M8 ${frameHeight - 42}L8 ${frameHeight - 8}L42 ${frameHeight - 8}M497 ${frameHeight - 42}L497 ${frameHeight - 8}L463 ${frameHeight - 8}"/>
        </svg>
        <div class="f-key-footer" style="top:${lowerTop + 116}px">${copy(data, 'note', '其他信息，暂时退后。')}</div>
      </div>`);
    },
    motion(ctx) {
      tween(ctx, '.f-key-back', { opacity: 0, y: 22, scale: 0.88 },
        { opacity: 1, y: 0, scale: 1, duration: 0.42, stagger: 0.13, ease: 'power2.out' }, 0.1);
      tween(ctx, '.f-keyword-label, .f-key-target', { opacity: 0, x: -55 },
        { opacity: 1, x: 0, duration: 0.6, stagger: 0.2, ease: 'power3.out' }, 0.15);
      tween(ctx, '.f-key-back', { opacity: 1, scale: 1 },
        { opacity: 0.3, scale: 0.92, duration: 0.45, ease: 'power2.inOut', immediateRender: false }, 1.65);
      tween(ctx, '.f-key-target', { scale: 1 },
        { scale: 1.08, duration: 0.6, ease: 'power3.inOut', immediateRender: false }, 1.65);
      draw(ctx, '.f-key-frame path', 1.95, 0.58);
      tween(ctx, '.f-key-footer', { opacity: 0, y: 12 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power1.out' }, 2.35);
      exit(ctx, '.f-keywords');
    }
  };

  M.L05 = {
    render(data) {
      const main = title(data, '制作参数');
      const rows = [['时长', '06 秒'], ['画幅', '1920 × 1080'], ['重点', '01 个']];
      const variant = data && data.fine ? ' fine' : '';
      return layer('f-facts-scene', B.box(105, 250, 570, `
        ${heading(main, 'f-facts-heading', [42, 35, 30])}
        <div class="f-facts-demo">演示数字 · 可替换字段与单位</div>
        <div class="f-facts-table">${rows.map(([label, value], i) => `<div class="f-facts-row"><span class="f-facts-label">${label}</span><span class="f-facts-value${i === 1 ? ' f-facts-resolution' : ''}">${value}</span></div>`).join('')}</div>
      `, `glass f-facts${variant}`));
    },
    motion(ctx) {
      const card=ctx.q('.f-facts')[0],side=card.offsetLeft+card.offsetWidth/2<=960?1:-1;
      ctx.tl.set(card,{transformOrigin:side===1?'0% 100%':'100% 100%'},0);
      tween(ctx, '.f-facts', { x: -100*side, rotationY: 13*side, rotationX:3, rotation:0, opacity: 0 },
        { x: 0, rotationY: 6*side, rotationX:4, rotation:0, opacity: 1, duration: 0.85, ease: 'power3.out' }, 0.1);
      tween(ctx, '.f-facts-row', { x: -20, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.45, stagger: 0.22, ease: 'power2.out' }, 0.6);
      tween(ctx, '.f-facts-value', { color: '#f5f6f2' },
        { color: '#d7ff48', duration: 0.3, stagger: 0.18, ease: 'power1.out', immediateRender: false }, 1.75);
      exit(ctx, '.f-facts');
    }
  };

  M.L06 = {
    render(data) {
      const main = title(data, '这一把吉他');
      const mainSize = fit(main, 44, 36, 30);
      const panelHeight = Math.max(180, 102 + Math.ceil(main.length * mainSize / 420) * mainSize * 1.25);
      return layer('f-object-scene', `<div class="plate glass f-object-label" style="left:110px;top:205px;width:480px;height:${panelHeight}px">
        <div class="f-object-kicker kicker">画面里的对象</div>
        ${heading(main, 'f-object-title', [44, 36, 30])}
      </div>
        <svg class="f-object-map" viewBox="0 0 1920 1080" aria-hidden="true">
          <path class="f-object-link" d="M518 ${205 + panelHeight}L518 459L377 572"/>
          <circle class="f-object-ring" cx="377" cy="572" r="24"/>
          <circle class="f-object-dot" cx="377" cy="572" r="5"/>
        </svg>`);
    },
    motion(ctx) {
      tween(ctx, '.f-object-label', { opacity: 0, x: -55 },
        { opacity: 1, x: 0, duration: 0.62, ease: 'power3.out' }, 0.1);
      draw(ctx, '.f-object-link', 0.82, 0.65);
      tween(ctx, '.f-object-ring', { opacity: 0, scale: 1.8, svgOrigin: '377 572' },
        { opacity: 1, scale: 1, duration: 0.4, ease: 'power2.out' }, 1.44);
      tween(ctx, '.f-object-dot', { opacity: 0, scale: 0, svgOrigin: '377 572' },
        { opacity: 1, scale: 1, duration: 0.25, ease: 'power2.out' }, 1.5);
      exit(ctx, '.f-object-scene');
    }
  };

  M.L07 = {
    render(data) {
      const question = title(data, '为什么要先讲清楚？');
      const size=fit(question,52,44,36),h=Math.max(174,76+Math.ceil(question.length*size/479)*size*1.34);
      const shape=`M58 1H497C529 1 554 26 554 58V${h-58}C554 ${h-36} 548 ${h-21} 534 ${h-11}C539 ${h+1} 558 ${h+17} 589 ${h+29}C562 ${h+24} 541 ${h+15} 526 ${h-2}C517 ${h-1} 509 ${h-1} 497 ${h-1}H58C26 ${h-1} 1 ${h-26} 1 ${h-58}V58C1 26 26 1 58 1Z`;
      return layer('f-glass-question-scene', `<div class="f-glass-question" style="height:${h+31}px">
        <div class="glass f-question-material" data-glass-path="${shape}" style="clip-path:path('${shape}');height:${h+31}px"></div>
        <div class="f-question-content" style="height:${h}px">${heading(question, 'f-glass-question-copy', [52,44,36])}</div>
      </div>`);
    },
    motion(ctx) {
      tween(ctx, '.f-glass-question', { opacity: 0, x: -70, rotation: -4, scale: 0.9 },
        { opacity: 1, x: 0, rotation: -1, scale: 1, duration: 0.8, ease: 'power3.out' }, 0.12);
      tween(ctx, '.f-glass-question-copy', { opacity: 0, y: 18 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }, 0.6);
      exit(ctx, '.f-glass-question', 5.25, { rotation: -1 });
    }
  };

  M.L08 = {
    render(data) {
      const first = title(data, '这一步真的有必要吗？');
      const bubble=(text,cls)=>{
        const size=fit(text,43,39,34);
        const units=Array.from(text).reduce((n,c)=>n+(/[^\x00-\xff]/.test(c)?1:.55),0);
        const width=Math.min(545,Math.max(300,Math.ceil(units*size)+72));
        const lines=Math.max(1,Math.ceil(units*size/(width-72)));
        const h=Math.max(116,Math.ceil(lines*size*1.32+52)),r=Math.min(58,h/2);
        const shape=`M${r} 1H${width-r}Q${width-1} 1 ${width-1} ${r}V${h-r}Q${width-1} ${h-1} ${width-r} ${h-1}H62L9 ${h+23}Q0 ${h+27} 4 ${h+17}L18 ${h-22}Q1 ${h-39} 1 ${h-r}V${r}Q1 1 ${r} 1Z`;
        return `<div class="f-comment ${cls}" style="width:${width}px;min-height:${h}px"><svg class="f-comment-shape" viewBox="0 0 ${width} ${h+28}" style="height:${h+28}px" aria-hidden="true"><path d="${shape}"/></svg><div class="f-comment-copy" style="font-size:${size}px">${B.esc(text)}</div></div>`;
      };
      return layer('f-comments-scene', `<div class="f-comments">
        ${bubble(first,'f-comment-first')}
        ${bubble(String(data?.second||'看完就能记住吗？'),'f-comment-second')}
      </div>`);
    },
    motion(ctx) {
      tween(ctx, '.f-comment-first', { opacity: 0, x: -70, y: -15, scale: 0.9, rotation: -4 },
        { opacity: 1, x: 0, y: 0, scale: 1, rotation: 0, duration: 0.62, ease: 'power3.out' }, 0.12);
      tween(ctx, '.f-comment-second', { opacity: 0, x: 48, y: 40, scale: 0.92, rotation: 3 },
        { opacity: 1, x: 0, y: 0, scale: 1, rotation: 0, duration: 0.65, ease: 'power3.out' }, 1.08);
      exit(ctx, '.f-comments');
    }
  };

  M.L09 = {
    render(data) {
      const answer = title(data, '让重点更好懂，才是高级。');
      return layer('f-response-scene', `<div class="f-dialog-question">
        <div class="f-dialog-kicker">追问</div>
        <div class="f-dialog-question-copy">${copy(data, 'question', '是不是越复杂越高级？')}</div>
      </div>
      ${B.box(1270, 435, 500, `<div class="f-dialog-kicker lime">回应</div>
        ${heading(answer, 'f-dialog-answer-copy', [48, 42, 34])}
        <svg class="f-dialog-answer-line" viewBox="0 0 420 28" aria-hidden="true"><path d="M5 18Q205 7 415 14"/></svg>
      `, 'glass f-dialog-answer')}`);
    },
    motion(ctx) {
      tween(ctx, '.f-dialog-question', { opacity: 0, x: -65, scale: 0.93 },
        { opacity: 1, x: 0, scale: 1, duration: 0.65, ease: 'power3.out' }, 0.12);
      tween(ctx, '.f-dialog-question', { opacity: 1, scale: 1 },
        { opacity: 0.48, scale: 0.94, duration: 0.45, ease: 'power2.inOut', immediateRender: false }, 2.15);
      tween(ctx, '.f-dialog-answer', { opacity: 0, x: 70, y: 24, scale: 0.94 },
        { opacity: 1, x: 0, y: 0, scale: 1, duration: 0.7, ease: 'power3.out' }, 2.12);
      draw(ctx, '.f-dialog-answer-line path', 2.92, 0.5);
      exit(ctx, '.f-dialog-question', 5.25, { opacity: 0.48 });
      exit(ctx, '.f-dialog-answer', 5.3);
    }
  };
}());
