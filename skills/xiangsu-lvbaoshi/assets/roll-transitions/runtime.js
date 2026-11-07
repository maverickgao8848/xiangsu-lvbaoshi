/* Approved 01 glass slide and 02 lime leak. Visual shells only; no media seeking. */
window.GLRollTransition = {
  apply(tl, kind, hostSel, bSel, fxSel, blankSel, cut, d, incoming) {
    const host=document.querySelector(hostSel), b=document.querySelector(bSel);
    const fx=document.querySelector(fxSel), blank=document.querySelector(blankSel);
    const start=cut-d/2, end=cut+d/2, sign=incoming?1:-1;
    if (kind==='lime-leak') {
      const layer=fx.querySelector('.film-fx'), node=name=>layer.querySelector('.film-'+name);
      tl.fromTo(layer,{opacity:0},{opacity:1,duration:.001,immediateRender:false},start);
      for (const [name,peak] of [['vignette',.85],['dust',.22],['grain',.08],['scratches',.05],['gate',.05]]) {
        tl.fromTo(node(name),{opacity:0},{opacity:peak,duration:d*.22,ease:'power2.out',immediateRender:false},start);
        tl.to(node(name),{opacity:0,duration:d*.28,ease:'power2.in'},start+d*.72);
      }
      tl.fromTo(node('dim'),{opacity:0},{opacity:.38,duration:d*.3,ease:'power2.in',immediateRender:false},start);
      tl.to(node('dim'),{opacity:.25,duration:d*.22},start+d*.3);
      tl.to(node('dim'),{opacity:0,duration:d*.48,ease:'power2.out'},start+d*.52);
      tl.fromTo(node('flash'),{opacity:0},{opacity:.30,duration:.035,ease:'power3.in',immediateRender:false},start+d*.43);
      tl.to(node('flash'),{opacity:0,duration:d*.4,ease:'power3.out'},start+d*.43+.035);
      tl.fromTo(node('dust'),{x:-sign*5,y:3,scale:1.018},{x:sign*13,y:-9,scale:1.04,duration:d,ease:'none',immediateRender:false},start);
      [[0,0],[21,-15],[-12,25],[27,8],[-18,-21],[9,17]].forEach((xy,i)=>tl.set(node('grain'),{x:xy[0]*sign,y:xy[1]},start+d*i/6));
      tl.fromTo(node('scratches'),{x:-sign*11},{x:sign*16,duration:d,ease:'steps(3)',immediateRender:false},start);
      tl.fromTo(node('leak'),{opacity:0,x:-sign*520,scale:1},{opacity:.94,x:0,scale:1.08,duration:d*.5,ease:'power2.in',immediateRender:false},start+d*.12);
      tl.to(node('leak'),{opacity:0,x:sign*620,scale:1.17,duration:d*.38,ease:'power2.out'},start+d*.62);
      tl.set(layer,{opacity:0},end);
      return;
    }
    if(kind!=='glass-slide') throw new Error('Unknown B-roll handoff style');
    const from=incoming?host:b, to=incoming?b:host, frame=fx.querySelector('.slide-rim'), sweep=fx.querySelector('.lime-sweep');
    tl.fromTo(sweep,{opacity:0,x:-sign*1300},{opacity:.7,x:sign*200,duration:d*.5,ease:'power2.inOut',immediateRender:false},start+d*.18);
    tl.to(sweep,{opacity:0,x:sign*1800,duration:d*.32,ease:'power2.out'},start+d*.68);
    tl.set(blank,{opacity:1},start);
    tl.set(b,{zIndex:21},start);
    if(incoming) tl.set(host,{zIndex:20},start);
    tl.fromTo(from,{x:0,scale:1},{x:0,scale:.91,duration:d*.22,ease:'power2.out',immediateRender:false},start);
    tl.to(from,{x:-sign*2200,duration:d*.28,ease:'power3.in'},start+d*.22);
    tl.fromTo(frame,{x:0,opacity:0,scale:1},{x:0,opacity:1,scale:.922,duration:d*.22,immediateRender:false},start);
    tl.to(frame,{x:-sign*2200,duration:d*.28,ease:'power3.in'},start+d*.22);
    if(!incoming) tl.set(host,{zIndex:20},cut);
    tl.fromTo(to,{x:sign*2200,scale:.91},{x:0,scale:.91,duration:d*.28,ease:'power3.out',immediateRender:false},cut);
    tl.to(to,{scale:1,duration:d*.22,ease:'power2.inOut'},cut+d*.28);
    tl.set(frame,{x:sign*2200,opacity:1,scale:.922},cut);
    tl.to(frame,{x:0,duration:d*.28,ease:'power3.out'},cut);
    tl.to(frame,{opacity:0,scale:1,duration:d*.22,ease:'power2.inOut'},cut+d*.28);
    if(incoming) tl.set(host,{x:0,scale:1,zIndex:0},cut);
    tl.set([host,b],{x:0,scale:1},end);
    tl.set(host,{zIndex:0},end);tl.set(b,{zIndex:20},end);
    tl.set(blank,{opacity:0},end);tl.set(frame,{opacity:0,x:0,scale:1},end);
  }
};
