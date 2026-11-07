(function(){
 const esc=GLBase.esc,isVideo=s=>/\.(webm|mp4)$/i.test(s);
 const media=(s,id,d,o=0,cls='',style='')=>isVideo(s)?`<video id="${esc(id)}" src="${esc(s)}" class="${cls}" data-start="0" data-duration="${d}" data-media-start="${o}" muted playsinline style="${style}"></video>`:`<img id="${esc(id)}" src="${esc(s)}" class="${cls}" alt="" style="${style}">`;
 function frame(m,id,d){return `<div class="glp-media-content">${m.crop?`<div class="glp-crop-window" data-crop="${esc(JSON.stringify({...m.crop,sourceWidth:m.sourceWidth,sourceHeight:m.sourceHeight}))}" style="position:absolute;overflow:hidden">${media(m.source,id,d,m.mediaStart||0,'','position:absolute;max-width:none;object-fit:fill')}</div>`:media(m.source,id,d,m.mediaStart||0)}</div>`;}
 function mapped(d,r){const[w,h]=d.sourceDimensions,s=Math.min(1920/w,1080/h);return{x:(1920-w*s)/2+r.x*s,y:(1080-h*s)/2+r.y*s,w:r.width*s,h:r.height*s};}
 function word(t,x,y,w,h,cls,i){return `<svg class="glp-fitted-word ${cls}" data-word-index="${i}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px" preserveAspectRatio="none" role="img" aria-label="${esc(t)}"><text x="0" y="0">${esc(t)}</text></svg>`;}
 function perspective(c,w,h){
  const source=[[0,0],[w,0],[w,h],[0,h]],rows=[];
  source.forEach(([x,y],i)=>{const {x:u,y:v}=c[i];rows.push([x,y,1,0,0,0,-u*x,-u*y,u],[0,0,0,x,y,1,-v*x,-v*y,v]);});
  for(let k=0;k<8;k++){let p=k;for(let i=k+1;i<8;i++)if(Math.abs(rows[i][k])>Math.abs(rows[p][k]))p=i;[rows[k],rows[p]]=[rows[p],rows[k]];const n=rows[k][k];if(Math.abs(n)<1e-10)throw Error('Degenerate panel corners');for(let j=k;j<9;j++)rows[k][j]/=n;for(let i=0;i<8;i++)if(i!==k){const f=rows[i][k];for(let j=k;j<9;j++)rows[i][j]-=f*rows[k][j];}}
  const[a,b,cx,d,e,f,g,hp]=rows.map(r=>r[8]);return `matrix3d(${a},${d},0,${g},${b},${e},0,${hp},0,0,1,0,${cx},${f},0,1)`;
 }
 function render(kind,d,duration,id){
  if(kind==='screen'){
   if(d.mode!=='callout')throw Error('Only circle-to-original-glass callout is retained');
   const r=mapped(d,d.region),c=d.card,ax=r.x+r.w/2,ay=r.y+r.h/2,left=c.x+272<ax,tx=left?c.x+545:c.x,ty=c.y+110,edge=ax+(left?-r.w/2:r.w/2),bend=left?tx+70:tx-70;
   const body=GLSampleModules.L02.render({title:d.label,definition:d.definition,note:d.note||''});
   return `<div class="glp-layer"><svg class="glp-circle-leader" viewBox="0 0 1920 1080" aria-hidden="true"><ellipse cx="${ax}" cy="${ay}" rx="${r.w/2}" ry="${r.h/2}"/><path d="M${edge} ${ay} H${bend} L${tx} ${ty}"/><circle cx="${edge}" cy="${ay}" r="5"/></svg><div class="glp-callout-shell" style="left:${c.x}px;top:${c.y}px">${body}</div></div>`;
  }
  if(kind==='companion')return `<div class="glp-layer">${['left','right'].filter(s=>d[s]).map(s=>{const o=d[s];return `<div class="glp-object ${s}" style="left:${o.x}px;top:${o.y}px;width:${o.size}px;height:${o.size+75}px"><div class="glp-object-inner"><img src="${esc(o.asset)}" alt=""><div class="glp-object-label" style="font-size:${Math.min(27,(o.size-12)/Math.max(1,o.label.length))}px">${esc(o.label)}</div></div></div>`;}).join('')}</div>`;
  const c=d.content||d;
  if(kind==='R01')return `<div class="glp-layer">${c.lines.map((r,i)=>`<div class="glp-fitted-word glp-lime-stack" data-word-index="${i}" style="left:${r.x}px;top:${r.y}px;width:${r.width}px;height:${r.height}px"><span class="glp-stack-copy">${esc(r.text)}</span></div>`).join('')}</div>`;
  if(kind==='R02')return `<div class="glp-layer"><div class="glp-perspective-media" style="left:0;top:0;width:${c.width}px;height:${c.height}px;transform:${perspective(c.corners,c.width,c.height)}"><div class="glp-media-heading">${esc(c.title)}</div><div class="glp-media-frame">${frame(c.media,id+'-insert',duration)}</div></div></div>`;
  if(kind==='R03')return `<div class="glp-layer">${c.items.map((r,i)=>`${r.caption?word(r.caption,r.x,r.y-76,r.captionWidth||220,38,'glp-white-caption',i):''}${word(r.label,r.x,r.y,r.width,r.height,'glp-lime-stage',i)}`).join('')}</div>`;
  if(kind==='R04'){const left=c.side==='left';return `<div class="glp-board"><div class="glp-board-kicker">${esc(c.kicker)}</div><h1 class="glp-board-title">${esc(c.title)}</h1><div class="glp-board-media" style="left:${left?600:78}px;width:1240px">${frame(c.media,id+'-main',duration)}</div><div class="glp-board-notes" style="left:${left?84:1390}px">${c.steps.map((s,i)=>`<div class="glp-note"><span>${String(i+1).padStart(2,'0')}</span><div>${esc(s)}</div><i></i></div>`).join('')}</div></div>`;}
  if(kind==='R05'){const left=c.hostSide==='left',center=c.hostSide==='center';return `<div class="glp-side-stage ${center?'glp-host-centered':''}"><div class="glp-host-original">${media(c.hostSource,id+'-host',duration,c.hostMediaStart||0,'glp-host-media')}</div><div class="glp-side-evidence" style="left:${left?1000:65}px"><div class="glp-side-title">${esc(c.title)}</div><div class="glp-side-media">${frame(c.media,id+'-evidence',duration)}</div><div class="glp-side-note">${esc(c.note)}</div></div></div>`;}
  throw Error('Unknown retained layer '+kind);
 }
 function fit(root){
  // R01 keeps the natural Chinese glyphs and one shared size across all lines.
  const copies=[...root.querySelectorAll('.glp-stack-copy')];
  const scale=copies.reduce((s,node)=>{const style=getComputedStyle(node),box=getComputedStyle(node.parentElement);return Math.min(s,parseFloat(box.width)/Math.max(1,parseFloat(style.width)),parseFloat(box.height)/Math.max(1,parseFloat(style.height)));},1);
  copies.forEach(node=>{node.style.transform=`scale(${scale})`;});
  const ctx=document.createElement('canvas').getContext('2d');root.querySelectorAll('svg.glp-fitted-word').forEach(svg=>{const node=svg.querySelector('text'),style=getComputedStyle(node);ctx.font=`${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;const b=ctx.measureText(node.textContent),left=-b.actualBoundingBoxLeft,right=b.actualBoundingBoxRight,top=-b.actualBoundingBoxAscent,bottom=b.actualBoundingBoxDescent;svg.setAttribute('viewBox',`${left-1.5} ${top-1.5} ${right-left+3} ${bottom-top+3}`);});root.querySelectorAll('.glp-crop-window').forEach(box=>{const r=JSON.parse(box.dataset.crop),p=box.parentElement,s=Math.min(p.offsetWidth/r.width,p.offsetHeight/r.height);Object.assign(box.style,{left:(p.offsetWidth-r.width*s)/2+'px',top:(p.offsetHeight-r.height*s)/2+'px',width:r.width*s+'px',height:r.height*s+'px'});Object.assign(box.firstElementChild.style,{left:-r.x*s+'px',top:-r.y*s+'px',width:r.sourceWidth*s+'px',height:r.sourceHeight*s+'px'});});}
 function fade(t,n,d){t.fromTo(n,{opacity:0},{opacity:1,duration:.28,ease:'power2.out'},0);t.to(n,{opacity:0,duration:.25,ease:'power1.in'},d-.25);}
 async function mount(root,id,kind,data,duration){
  await document.fonts.ready;await Promise.all([...root.querySelectorAll('img')].map(i=>i.decode()));fit(root);
  const q=s=>[...root.querySelectorAll(s)],tl=gsap.timeline({paused:true}),c=data.content||data;
  if(kind==='screen'){
   GLGlass.install(root,id);q('.glp-circle-leader ellipse,.glp-circle-leader path').forEach((p,i)=>{const n=p.getTotalLength();p.style.strokeDasharray=n;tl.fromTo(p,{strokeDashoffset:n},{strokeDashoffset:0,duration:.48,ease:'power2.out'},i*.35);});
   const child=gsap.timeline({paused:true});GLSampleModules.L02.motion({root,tl:child,q,duration:6,data:{},signature:null});tl.add(child.paused(false).timeScale(6/Math.max(1,duration-.45)),.45);fade(tl,q('.glp-circle-leader'),duration);
  }else if(kind==='companion'){
   for(const side of ['left','right']){const o=data[side];if(!o)continue;const outer=q('.glp-object.'+side),inner=q('.glp-object.'+side+' .glp-object-inner'),dir=side==='left'?-1:1;fade(tl,outer,duration);tl.fromTo(outer,{x:dir*52,scale:.86},{x:0,scale:1,duration:.65,ease:'power3.out'},side==='right'?.12:0);const hold=Math.max(.1,duration-1.4);if(o.motion==='float')tl.fromTo(inner,{y:4},{y:-11,duration:hold/2,yoyo:true,repeat:1,ease:'sine.inOut'},.9);if(o.motion==='nod')tl.fromTo(inner,{rotationY:-dir*6},{rotationY:dir*8,duration:hold/2,yoyo:true,repeat:1,ease:'sine.inOut'},.9);if(o.motion==='pulse')tl.fromTo(inner,{scale:1},{scale:1.045,duration:hold/2,yoyo:true,repeat:1,ease:'sine.inOut'},.9);}
  }else if(kind==='R01'||kind==='R03'){
   q('.glp-fitted-word').forEach(el=>{const i=Number(el.dataset.wordIndex),at=(kind==='R01'?c.lines[i].at:c.items[i].at)||0;tl.fromTo(el,{opacity:0,y:16},{opacity:1,y:0,duration:.28,ease:'power2.out'},at);tl.to(el,{opacity:0,duration:.25},duration-.25);});
  }else if(kind==='R02'){fade(tl,q('.glp-perspective-media'),duration);tl.fromTo(q('.glp-media-frame'),{y:36,scale:.94},{y:0,scale:1,duration:.75,ease:'power3.out'},0);tl.fromTo(q('.glp-media-heading'),{opacity:0,y:6},{opacity:1,y:0,duration:.3},.22);
  }else if(kind==='R04'){fade(tl,q('.glp-board-kicker,.glp-board-title,.glp-board-media'),duration);tl.fromTo(q('.glp-board-media'),{y:24},{y:0,duration:.7,ease:'power3.out'},.1);q('.glp-note').forEach((el,i)=>{tl.fromTo(el,{opacity:0,x:20},{opacity:1,x:0,duration:.4},.6+i*.65);tl.fromTo(el.querySelector('i'),{scaleX:0},{scaleX:1,duration:.5,ease:'power2.out'},.8+i*.65);});
  }else if(kind==='R05'){fade(tl,q('.glp-side-evidence'),duration);tl.fromTo(q('.glp-side-evidence'),{x:c.hostSide==='left'?35:-35},{x:0,duration:.7,ease:'power3.out'},.2);}
  tl.to({}, {duration:.01},duration-.01);window.__timelines=window.__timelines||{};window.__timelines[id]=tl;tl.seek(0,false);return true;
 }
 window.GLProduction={render,mount,mapped};
}());
