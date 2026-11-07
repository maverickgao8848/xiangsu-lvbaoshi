(function(){
  let ctx,buffers=new Map(),sources=[],generation=0;
  function stop(){generation++;sources.forEach(source=>{try{source.stop();}catch{}});sources=[];}
  function cues(preset,kit){
    if(preset==='none'||kit==='mute')return [];
    const variant=SavedMotionCatalog.variants.find(item=>item.id===preset);
    return SavedMotionCatalog.cues[preset][kit==='auto'?variant.kit:kit];
  }
  async function play(timeline,preset,kit,volume,start){
    stop();const token=generation,events=cues(preset,kit);
    if(events.length){
      ctx=ctx||new AudioContext();await ctx.resume();
      await Promise.all([...new Set(events.map(event=>event.file))].map(async file=>{
        if(!buffers.has(file)){const response=await fetch(file);if(!response.ok)throw Error('声音文件加载失败');buffers.set(file,await ctx.decodeAudioData(await response.arrayBuffer()));}
      }));
      if(generation!==token)return false;
      const now=ctx.currentTime+.025,rate=timeline.timeScale();
      for(const event of events.filter(event=>event.at>=start)){
        const source=ctx.createBufferSource(),gain=ctx.createGain();source.buffer=buffers.get(event.file);gain.gain.value=event.volume*volume;source.connect(gain).connect(ctx.destination);source.start(now+(event.at-start)/rate);sources.push(source);
      }
    }
    if(generation!==token)return false;timeline.play(start);return true;
  }
  window.GLSound={play,stop,cues,state:()=>({loaded:buffers.size,scheduled:sources.length})};
}());
