(function(){
  const B=window.GLBase;
  window.GLSampleModules.L31={
    render(data,A){
      const source=data.source||A+'material-source.png';
      const regions=data.regions||window.GLMaterialRegions;
      if(!regions?.length)throw new Error('Material highlight needs source-pixel regions.');
      return `<div class="h-heading"><span class="kicker">素材原图 / 多处词组标记</span><h2>${B.esc(data.title||'把重点留在原来的位置')}</h2></div><div class="h-material"><img class="h-original" src="${B.esc(source)}" alt="自编示例文档的原始截图">${regions.map((r,index)=>`<div class="h-mark" data-group="${r.group}" style="left:${r.x}px;top:${r.y}px;width:${r.width}px;height:${r.height}px"><img src="${B.esc(source)}" alt="" aria-hidden="true" style="left:${-r.x}px;top:${-r.y}px"></div>`).join('')}</div><p class="h-note">来源：自编示例文档 · 高亮保留原图字形与位置 · 换素材后重新定位</p>`;
    },
    motion({q,tl}){
      tl.fromTo(q('.h-heading,.h-material'),{opacity:0,y:16},{opacity:1,y:0,duration:.65,stagger:.12,ease:'power3.out'},.1);
      q('.h-mark').forEach(mark=>tl.fromTo(mark,{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.55,ease:'power2.inOut'},1.05+Number(mark.dataset.group)*.48));
      tl.fromTo(q('.h-note'),{opacity:0},{opacity:1,duration:.4},2.55);
    }
  };
}());
