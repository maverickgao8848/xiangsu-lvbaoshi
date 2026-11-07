(function(){
 function mount(root,variant,subjectId){
  const s=SignatureCatalog.subjects.find(x=>x.id===subjectId);
  const shell=root.querySelector('.sig-shell'),content=root.querySelector('.sig-content'),mask=root.querySelector('.sig-mask');
  const line=root.querySelector('.sig-line'),shutter=root.querySelector('.sig-shutter-line');
  // The original semantic motion supplies one settled pose. Signature motion
  // owns only its outer envelope, so it cannot overwrite inner module channels.
  const settled=gsap.timeline({paused:true});
  GLSampleModules[s.sample].motion({root,tl:settled,q:sel=>Array.from(content.querySelectorAll(sel)),data:{title:s.title},duration:6});
  settled.seek(3,false);settled.kill();
  const t=gsap.timeline({paused:true});
  const endX=1835-(s.x+s.w/2),endY=95-(s.y+s.h/2);
  const pose={x:0,y:0,scale:1,rotation:0,rotationY:0,opacity:1};
  const move=(from,to,at)=>t.fromTo(shell,from,{...to,immediateRender:false},at);
  t.set(shell,{...pose,opacity:0,transformOrigin:'50% 50%',transformPerspective:1800},0);
  if(['B','D','F'].includes(variant))t.fromTo(shell,{opacity:0},{opacity:1,duration:.03,immediateRender:false},.12);
  if(variant==='A'){
   move({x:-170,y:140,scale:.025,rotation:-14,opacity:0},{...pose,duration:.78,ease:'power3.out'},.15);
   t.to(shell,{x:-17,y:14,scale:1.035,duration:.12,ease:'power2.inOut'},4.70);
   t.to(shell,{x:endX,scale:.008,rotation:17,duration:.74,ease:'power3.in'},4.82);
   t.to(shell,{y:endY,duration:.74,ease:'power2.out'},4.82);
   t.to(shell,{opacity:0,duration:.1},5.50);
  }else if(variant==='B'){
   t.fromTo(mask,{clipPath:'inset(49.8% 0 49.8% 0)'},{clipPath:'inset(0% 0 0% 0)',duration:.43,ease:'power3.out'},.26);
   t.fromTo(shutter,{opacity:0,scaleX:.1},{opacity:1,scaleX:1,duration:.16},.12);
   t.to(shutter,{opacity:0,duration:.18},.42);
   t.to(mask,{clipPath:'inset(49.8% 0 49.8% 0)',duration:.3,ease:'power3.in'},4.70);
   t.fromTo(shutter,{opacity:0,scaleX:1},{opacity:1,duration:.08,immediateRender:false},4.93);
   t.to(mask,{opacity:0,duration:.06},5.0);
   t.to(shutter,{scaleX:0,opacity:0,duration:.25,ease:'power2.in'},5.02);
  }else if(variant==='C'){
   move({rotationY:79,x:75,y:18,scale:.9,opacity:0},{...pose,duration:.87,ease:'power3.out'},.15);
   t.to(shell,{rotationY:-86,x:-85,scale:.93,duration:.66,ease:'power3.in'},4.70);
   t.to(shell,{opacity:0,duration:.15},5.22);
  }else if(variant==='D'){
   t.fromTo(line,{scaleY:0,opacity:1},{scaleY:1,duration:.3,ease:'power2.out'},.15);
   t.fromTo(mask,{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.62,ease:'power3.out'},.35);
   t.to(line,{opacity:0,duration:.14},.86);
   t.to(mask,{clipPath:'inset(0 0 0 100%)',duration:.5,ease:'power3.inOut'},4.70);
   t.fromTo(line,{x:0,opacity:0,scaleY:1},{x:s.w,opacity:1,duration:.5,ease:'power3.inOut',immediateRender:false},4.70);
   t.to(line,{scaleY:0,opacity:0,duration:.28,ease:'power2.in'},5.2);
  }else if(variant==='E'){
   move({y:75,scale:.88,rotation:-2,opacity:0},{...pose,duration:.7,ease:'back.out(1.25)'},.15);
   t.to(shell,{scale:.94,y:14,duration:.12,ease:'power2.in'},4.7);
   t.to(shell,{y:-155,scale:.85,opacity:0,duration:.48,ease:'power3.in'},4.82);
  }else if(variant==='F'){
   const selectors=s.id==='glass'?['.f-definition','.f-lens']:s.id==='bubble'?['.f-comment-first','.f-comment-second']:['.x-chapter-num','.x-chapter-copy'];
   selectors.forEach((sel,i)=>{
    const nodes=Array.from(content.querySelectorAll(sel));
    t.fromTo(nodes,{x:-55-i*25,y:35+i*15,rotationY:-15-i*6,opacity:0},{x:0,y:0,rotationY:0,opacity:1,duration:.65,ease:'power3.out'},.15+i*.09);
    t.to(nodes,{x:endX,y:endY,scale:.01,rotation:12,opacity:0,duration:.68,ease:'power3.in'},4.7+i*.09);
   });
  }
  t.to(shell,{opacity:0,duration:.08},5.65);
  t.to({}, {duration:.01},5.99);
  // HyperFrames moves data-composition-id from the authored inner root to
  // its host when assembling. Register by the stable instance ID.
  const compositionId=`sig-${variant}-${subjectId}`;
  window.__timelines=window.__timelines||{};window.__timelines[compositionId]=t;
  t.seek(0,false);return t;
 }
 window.SignatureMotion={mount};
}());
