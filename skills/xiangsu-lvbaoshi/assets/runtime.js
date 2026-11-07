(function(){
  // HyperFrames can inline this script; then its src is empty or a data URL.
  const scriptSource=document.currentScript?.getAttribute('src');
  const assetPrefix=scriptSource&&!scriptSource.startsWith('data:')?scriptSource.replace(/[^/]*$/,''):'assets/';
  function setHostFinish(root,config={enabled:false}){
    if(!config||typeof config!=='object'||typeof config.enabled!=='boolean')throw new Error('hostFinish.enabled must be boolean.');
    if(config.preset!==undefined&&config.preset!=='soft-edge-v1')throw new Error('Unknown hostFinish preset.');
    root.dataset.hostFinish=config.enabled?'soft-edge-v1':'off';
    root.style.setProperty('--host-edge-shadow',`url("${assetPrefix}host-edge-shadow/soft-edge-v1.png")`);
  }
  function mount(root,id,data={}){
    const def=window.GLSampleModules[id];
    if(!def)throw new Error('Missing sample module '+id);
    setHostFinish(root,data.hostFinish);
    const tl=gsap.timeline({paused:true});
    const q=s=>Array.from(root.querySelectorAll(s));
    const compositionId=data.compositionId||id;
    GLGlass.install(root,compositionId);
    const signature=data.signature&&data.signature!=='none'&&id!=='L30'?data.signature:null;
    def.motion({root,tl,q,duration:6,data,signature});
    if(signature)GLEnvelope.apply(root,tl,id,signature,data.exitTreatment);
    else tl.fromTo(q('.foreground'),{opacity:1},{opacity:0,duration:.38,ease:'power1.in'},5.55);
    tl.to({}, {duration:.01},5.99);
    window.__timelines=window.__timelines||{};window.__timelines[compositionId]=tl;
    tl.seek(0,false);return tl;
  }
  window.GLRuntime={mount,setHostFinish};
}());
