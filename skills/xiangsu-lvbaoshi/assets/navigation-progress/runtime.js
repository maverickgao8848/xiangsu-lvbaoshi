(function () {
  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character];
    });
  }

  function render(chapters) {
    return '<div class="bar" role="progressbar" aria-label="章节进度">' +
      chapters.map(function (chapter) {
        var length = Number(chapter.end) - Number(chapter.start);
        return '<div class="segment" style="--duration:' + length + '">' +
          '<i class="fill"></i><i class="head"></i>' +
          '<span class="label"><b>' + escapeHtml(chapter.number) + '</b><em>' + escapeHtml(chapter.title) + '</em></span>' +
        '</div>';
      }).join('') +
    '</div>';
  }

  function cornerHtml(chapters) {
    return '<div class="gl-corner-items">' + chapters.map(function (chapter) {
      return '<div class="gl-corner-item">' +
        '<b>' + escapeHtml(chapter.number) + '</b><i aria-hidden="true"></i>' +
        '<h2>' + escapeHtml(chapter.title) + '</h2>' +
      '</div>';
    }).join('') + '</div><span class="gl-corner-line"></span>';
  }

  function mount(root, data, duration) {
    var host = root.querySelector('.gl-progress');
    if (!host) throw new Error('navigation-progress root missing');
    host.innerHTML = render(data.chapters);
    var corner = document.createElement('div');
    corner.className = 'gl-corner';
    corner.setAttribute('aria-hidden', 'true');
    corner.innerHTML = cornerHtml(data.chapters);
    root.appendChild(corner);
    var timeline = gsap.timeline({ paused: true });
    var segments = host.querySelectorAll('.segment');
    var cornerItems = corner.querySelectorAll('.gl-corner-item');
    var cornerLine = corner.querySelector('.gl-corner-line');
    gsap.set(cornerItems, { autoAlpha: 0, x: -14 });
    data.chapters.forEach(function (chapter, index) {
      var segment = segments[index];
      var fill = segment.querySelector('.fill');
      var head = segment.querySelector('.head');
      var label = segment.querySelector('.label');
      var number = label.querySelector('b');
      var length = Number(chapter.end) - Number(chapter.start);
      timeline.fromTo(fill, { scaleX: 0 }, { scaleX: 1, duration: length, ease: 'none' }, chapter.start);
      timeline.set(head, { opacity: 1 }, chapter.start);
      // Computed width is in the segment's local coordinate space, including
      // fractional flex widths and excluding any scale applied to the stage.
      var segmentWidth = parseFloat(getComputedStyle(segment).width);
      timeline.fromTo(head, { x: 0 }, { x: segmentWidth, duration: length, ease: 'none' }, chapter.start);
      timeline.set(head, { opacity: 0 }, chapter.end);
      timeline.set(label, { color: 'rgba(252,254,255,1)' }, chapter.start);
      timeline.set(number, { color: 'rgba(255,255,255,.88)' }, chapter.start);
      if (index < data.chapters.length - 1) {
        timeline.set(label, { color: 'rgba(244,249,250,.90)' }, chapter.end);
        timeline.set(number, { color: 'rgba(244,249,250,.80)' }, chapter.end);
      }
      // Corner badge: only the active chapter is visible; the lime underline sweeps once per chapter.
      if (index > 0) timeline.set(cornerItems[index - 1], { autoAlpha: 0 }, chapter.start);
      timeline.fromTo(cornerItems[index], { autoAlpha: 0, x: -14 },
        { autoAlpha: 1, x: 0, duration: .5, ease: 'power2.out' }, chapter.start);
      timeline.fromTo(cornerLine, { scaleX: 0 }, { scaleX: 1, duration: .55, ease: 'power2.inOut' }, chapter.start);
      timeline.to(cornerLine, { scaleX: 0, duration: .35, ease: 'power2.in' }, chapter.start + 1.1);
    });
    (data.hide || []).forEach(function (range) {
      timeline.to(corner, { opacity: 0, duration: .25, ease: 'none' }, range[0]);
      timeline.to(corner, { opacity: 1, duration: .35, ease: 'none' }, range[1]);
    });
    timeline.to({}, { duration: 0.01 }, Math.max(0, Number(duration) - 0.01));
    return timeline;
  }

  window.GLNavProgress = { render: render, mount: mount };
}());
