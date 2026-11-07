(function () {
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const check = '<svg viewBox="0 0 64 64" class="tick" aria-hidden="true"><path d="M12 34L26 48L53 15" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const box = (x,y,w,body,cls='glass') => `<div class="plate ${cls}" style="left:${x}px;top:${y}px;width:${w}px">${body}</div>`;
  window.GLBase = {esc,check,box};
  window.GLSampleModules = window.GLSampleModules || {};
}());
