(function(){
  function bounds(root){
    const canvas=root.getBoundingClientRect(),nodes=Array.from(root.querySelectorAll('.foreground *'));
    const rects=nodes.filter(node=>{
      const style=getComputedStyle(node);if(style.display==='none'||Number(style.opacity)<.03)return false;
      if(node.tagName.toLowerCase()==='path'||node.tagName.toLowerCase()==='circle')return true;
      return Array.from(node.childNodes).some(child=>child.nodeType===3&&child.textContent.trim())||node.tagName==='IMG'||
        style.backgroundImage!=='none'||!['transparent','rgba(0, 0, 0, 0)'].includes(style.backgroundColor)||parseFloat(style.borderTopWidth)>0;
    }).map(node=>node.getBoundingClientRect()).filter(rect=>rect.width&&rect.height);
    if(!rects.length)throw new Error('No visible subject for motion envelope.');
    const x=Math.max(0,Math.min(...rects.map(r=>r.left-canvas.left))-48),y=Math.max(0,Math.min(...rects.map(r=>r.top-canvas.top))-48);
    const right=Math.min(1920,Math.max(...rects.map(r=>r.right-canvas.left))+48),bottom=Math.min(1080,Math.max(...rects.map(r=>r.bottom-canvas.top))+48);
    return {x,y,w:right-x,h:bottom-y};
  }
  function apply(root,tl,id,variant,exitTreatment){
    const localExit=exitTreatment==='domain-warp';
    if(localExit&&!['B','D'].includes(variant))throw Error('Domain Warp exit is currently composed with B/D entrances.');
    if(!variant||variant==='none'||id==='L30')return;
    if(!['A','B','C','D'].includes(variant))throw new Error('Available motions: A, B, C, D.');
    tl.seek(3.6,false);
    // A paired object has its own local collapse region, independent of the card.
    const companions=variant==='A'?[...root.querySelectorAll('.gl-companion-object')].map(node=>{
      const rect=node.getBoundingClientRect(),canvas=root.getBoundingClientRect();
      const item={node,x:rect.left-canvas.left,y:rect.top-canvas.top,w:rect.width,h:rect.height};
      node.remove();return item;
    }):[];
    const s=bounds(root);tl.seek(0,false);
    const foreground=root.querySelector('.foreground'),content=document.createElement('div');content.className='env-content';
    while(foreground.firstChild)content.append(foreground.firstChild);
    content.style.cssText=`left:${-s.x}px;top:${-s.y}px`;
    const shell=document.createElement('div');shell.className='env-shell';shell.style.cssText=`left:${s.x}px;top:${s.y}px;width:${s.w}px;height:${s.h}px`;
    const mask=document.createElement('div');mask.className='env-mask';mask.append(content);shell.append(mask);
    const line=document.createElement('div');line.className='env-line';const shutter=document.createElement('div');shutter.className='env-shutter';shell.append(line,shutter);foreground.append(shell);
    // Collapse into the subject's own upper-right shoulder (inside its bounds).
    // Relative coordinates also keep circular subjects anchored on their rim.
    const endX=Math.min(s.w*.18,140),endY=-Math.min(s.h*.18,90),pose={x:0,y:0,scale:1,rotation:0,rotationY:0,opacity:1};
    shell.dataset.magnetX=String(s.x+s.w/2+endX);shell.dataset.magnetY=String(s.y+s.h/2+endY);
    const move=(from,to,at)=>tl.fromTo(shell,from,{...to,immediateRender:false},at);
    tl.set(shell,{...pose,opacity:0,transformOrigin:'50% 50%',transformPerspective:1800},0);
    if(['B','D'].includes(variant))tl.fromTo(shell,{opacity:0},{opacity:1,duration:.03,immediateRender:false},.12);
    if(variant==='A'){
      move({x:-170,y:140,scale:.025,rotation:-14,opacity:0},{...pose,duration:.78,ease:'power3.out'},.15);
      tl.to(shell,{x:-17,y:14,scale:1.035,duration:.12,ease:'power2.inOut'},4.70);
      tl.to(shell,{x:endX,scale:.008,rotation:17,duration:.74,ease:'power3.in'},4.82);
      tl.to(shell,{y:endY,duration:.74,ease:'power2.out'},4.82);tl.to(shell,{opacity:0,duration:.1},5.50);
      companions.forEach(item=>{
        const local=document.createElement('div');local.className='env-companion';
        local.style.cssText='position:absolute;inset:0';local.append(item.node);foreground.append(local);
        const dx=Math.min(item.w*.18,140),dy=-Math.min(item.h*.18,90);
        tl.set(local,{transformOrigin:`${item.x+item.w/2}px ${item.y+item.h/2}px`,opacity:0},0);
        tl.fromTo(local,{x:-Math.min(item.w*.18,90),y:Math.min(item.h*.18,64),scale:.025,rotation:-14,opacity:0},{...pose,duration:.78,ease:'power3.out',immediateRender:false},.15);
        tl.to(local,{x:-9,y:7,scale:1.035,duration:.12,ease:'power2.inOut'},4.70);
        tl.to(local,{x:dx,y:dy,scale:.008,rotation:17,duration:.74,ease:'power3.in'},4.82);
        tl.to(local,{opacity:0,duration:.1},5.50);
      });
    }else if(variant==='B'){
      tl.fromTo(mask,{clipPath:'inset(49.8% 0 49.8% 0)'},{clipPath:'inset(0% 0 0% 0)',duration:.43,ease:'power3.out'},.26);
      tl.fromTo(shutter,{opacity:0,scaleX:.1},{opacity:1,scaleX:1,duration:.16},.12);tl.to(shutter,{opacity:0,duration:.18},.42);
      if(!localExit){
      tl.to(mask,{clipPath:'inset(49.8% 0 49.8% 0)',duration:.3,ease:'power3.in'},4.70);
      tl.fromTo(shutter,{opacity:0,scaleX:1},{opacity:1,duration:.08,immediateRender:false},4.93);tl.to(mask,{opacity:0,duration:.06},5);
      tl.to(shutter,{scaleX:0,opacity:0,duration:.25,ease:'power2.in'},5.02);
      }
    }else if(variant==='C'){
      // Press the upper INNER corner away from the viewer. The opposite lower
      // corner anchors the card: left card -> right-top, right card -> left-top.
      const side=s.x+s.w/2<=960?1:-1;
      shell.dataset.foldSide=side===1?'left':'right';
      tl.set(shell,{transformOrigin:side===1?'0% 100%':'100% 100%'},0);
      move({rotationY:side*64,rotationX:16,x:side*16,y:10,scale:.96,opacity:0},{...pose,rotationX:0,duration:.87,ease:'power3.out'},.15);
      tl.to(shell,{rotationY:side*14,rotationX:6,duration:.16,ease:'power2.in'},4.70);
      tl.to(shell,{rotationY:side*65,rotationX:18,x:side*14,y:15,scale:.96,duration:.5,ease:'power3.in'},4.86);
      tl.to(shell,{opacity:0,duration:.15},5.22);
    }else if(variant==='D'){
      tl.fromTo(line,{scaleY:0,opacity:1},{scaleY:1,duration:.3,ease:'power2.out'},.15);
      tl.fromTo(mask,{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.62,ease:'power3.out'},.35);tl.to(line,{opacity:0,duration:.14},.86);
      if(!localExit){
      tl.to(mask,{clipPath:'inset(0 0 0 100%)',duration:.5,ease:'power3.inOut'},4.70);
      tl.fromTo(line,{x:0,opacity:0,scaleY:1},{x:s.w,opacity:1,duration:.5,ease:'power3.inOut',immediateRender:false},4.70);tl.to(line,{scaleY:0,opacity:0,duration:.28,ease:'power2.in'},5.2);
      }
    }
    if(!localExit)tl.to(shell,{opacity:0,duration:.08},5.65);tl.seek(0,false);
  }
  window.GLEnvelope={apply};
}());
