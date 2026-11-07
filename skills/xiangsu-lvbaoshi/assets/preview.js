(function(){
  function init(root,id,A){
    let content={},options={signature:'none'};
    function rebuild(){
      window.previewTimeline?.kill();root.querySelector('.foreground').innerHTML=GLSampleModules[id].render(content,A);
      window.previewTimeline=GLRuntime.mount(root,id,{...content,...options});window.previewMotion=options.signature;window.previewSeek(2.8);
    }
    window.previewSeek=t=>{window.previewTimeline.pause().seek(Math.max(0,Math.min(6,t)),false);return true;};
    window.previewSetTitle=value=>{content.title=value;rebuild();};
    window.previewSetMotion=value=>{options.signature=value;rebuild();};
    window.previewSetHostFinish=enabled=>{options.hostFinish={enabled};GLRuntime.setHostFinish(root,options.hostFinish);return true;};
    window.previewSetBackground=mode=>{root.querySelector('.background').className='background '+mode;};
    window.previewSetQuality=fine=>root.classList.toggle('fine',fine);
    window.previewReady=document.fonts.ready.then(()=>{rebuild();return true;});
  }
  window.GLPreview={init};
}());
