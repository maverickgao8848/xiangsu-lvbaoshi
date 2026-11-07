(function(){
  function nodes(root){
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),result=[];
    while(walker.nextNode()){
      const node=walker.currentNode;
      if(node.nodeValue.trim()&&!node.parentElement.closest('svg')&&!/^[\s↗→↓↑＋+−×·•]+$/.test(node.nodeValue))result.push(node);
    }
    return result;
  }
  function bind(root,content){
    const foreground=root.querySelector('.foreground'),text=nodes(foreground),images=[...foreground.querySelectorAll('img')];
    if(!Array.isArray(content.text)||content.text.length!==text.length||!Array.isArray(content.images)||content.images.length!==images.length)throw new Error('Production text/image slots must be filled exactly.');
    text.forEach((node,i)=>node.nodeValue=content.text[i]);
    images.forEach((node,i)=>{node.src=content.images[i];node.alt='';});
  }
  async function mount(root,id,templateId,content,duration,motion){
    await document.fonts.ready;
    bind(root,content);
    await Promise.all([...root.querySelectorAll('img')].map(img=>img.decode()));
    const child=GLRuntime.mount(root,templateId,{...content,compositionId:id,signature:motion});
    const master=gsap.timeline({paused:true});
    master.add(child.paused(false).timeScale(6/duration),0);
    window.__timelines[id]=master;
    if(content.exitTexture)await GLDomainWarpExit.attach(root,master,content,duration);
    master.seek(0,false);
    return true;
  }
  window.GLEditorial={mount};
}());
