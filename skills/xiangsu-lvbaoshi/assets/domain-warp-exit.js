/* Domain Warp Dissolve shader adapted from the installed HyperFrames catalog item.
 * Cascaded fbm(q -> r -> n) and warp defaults retained; output is the actual
 * foreground texture dissolving to alpha, with a restrained local lime edge.
 * No demo scenes, opaque fill, host texture, scene hold or full-screen overlay.
 */
(function(){
  const vertex='attribute vec2 a_pos;varying vec2 v_uv;void main(){v_uv=a_pos*.5+.5;v_uv.y=1.-v_uv.y;gl_Position=vec4(a_pos,0,1);}';
  const fragment=`precision highp float;
    varying vec2 v_uv;uniform sampler2D u_source;uniform float u_progress;
    uniform vec4 u_regions[4];uniform int u_count;uniform float u_noise,u_warp,u_edge,u_gain;
    uniform vec3 u_color;
    float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    float vnoise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*f*(f*(f*6.-15.)+10.);
      return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
    float fbm(vec2 p){float v=0.,a=.5;mat2 R=mat2(.8,.6,-.6,.8);
      for(int i=0;i<5;i++){v+=a*vnoise(p);p=R*p*2.02;a*=.5;}return v;}
    void main(){
      if(u_progress<=0.){gl_FragColor=texture2D(u_source,v_uv);return;}
      if(u_progress>=1.){gl_FragColor=vec4(0.);return;}
      vec4 box=vec4(0.,0.,1.,1.);bool found=false;
      for(int i=0;i<4;i++){if(i<u_count){vec4 b=u_regions[i];
        if(v_uv.x>=b.x&&v_uv.y>=b.y&&v_uv.x<=b.x+b.z&&v_uv.y<=b.y+b.w){box=b;found=true;break;}}}
      if(!found){gl_FragColor=vec4(0.);return;}
      vec2 uv=(v_uv-box.xy)/box.zw;
      vec2 q=vec2(fbm(uv*u_noise),fbm(uv*u_noise+vec2(5.2,1.3)));
      vec2 r=vec2(fbm(uv*u_noise+q*4.+vec2(1.7,9.2)),fbm(uv*u_noise+q*4.+vec2(8.3,2.8)));
      float n=fbm(uv*u_noise+r*2.);
      vec2 warped=clamp(uv+(q-.5)*u_warp*u_progress,vec2(.001),vec2(.999));
      vec4 source=texture2D(u_source,box.xy+warped*box.zw);
      float remain=smoothstep(u_progress-u_edge,u_progress+u_edge,n);
      float rim=(1.-smoothstep(0.,u_edge*1.25,abs(n-u_progress)))*sin(u_progress*3.14159265);
      gl_FragColor=vec4(source.rgb+u_color*rim*u_gain,source.a*remain);
    }`;
  function program(gl){
    const compile=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);
      if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    const p=gl.createProgram();gl.attachShader(p,compile(gl.VERTEX_SHADER,vertex));gl.attachShader(p,compile(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));return p;
  }
  async function attach(root,timeline,data,duration){
    const image=new Image();image.src=data.exitTexture;await image.decode();
    if(image.naturalWidth!==1920||image.naturalHeight!==1080)throw Error('Exit texture must be a transparent 1920x1080 foreground.');
    const canvas=document.createElement('canvas');canvas.className='domain-warp-exit';canvas.width=1920;canvas.height=1080;
    canvas.style.cssText='position:absolute;inset:0;width:1920px;height:1080px;z-index:3;pointer-events:none;opacity:0';root.append(canvas);
    const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:false,preserveDrawingBuffer:true});
    if(!gl)throw Error('Domain Warp exit requires WebGL.');
    const p=program(gl);gl.useProgram(p);gl.viewport(0,0,1920,1080);
    const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
    const pos=gl.getAttribLocation(p,'a_pos');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
    const texture=gl.createTexture();gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);gl.uniform1i(gl.getUniformLocation(p,'u_source'),0);
    const regions=new Float32Array(16);data.exitRegions.forEach((b,i)=>regions.set([b.x/1920,b.y/1080,b.width/1920,b.height/1080],i*4));
    gl.uniform4fv(gl.getUniformLocation(p,'u_regions[0]'),regions);gl.uniform1i(gl.getUniformLocation(p,'u_count'),data.exitRegions.length);
    const settings=data.exitSettings;
    for(const [uniform,key] of [['u_noise','noiseScale'],['u_warp','warpScale'],['u_edge','edgeWidth'],['u_gain','edgeGain']])gl.uniform1f(gl.getUniformLocation(p,uniform),settings[key]);
    const color=settings.edgeColor.match(/[a-f\d]{2}/gi).map(v=>parseInt(v,16)/255);gl.uniform3fv(gl.getUniformLocation(p,'u_color'),color);
    const progress=gl.getUniformLocation(p,'u_progress'),foreground=root.querySelector('.foreground'),start=duration-settings.durationSec;
    const update=()=>{
      const time=timeline.time(),amount=time>=duration-.00001?1:Math.max(0,Math.min(1,(time-start)/settings.durationSec));root.dataset.exitProgress=String(amount);
      if(time<start){foreground.style.opacity='1';canvas.style.opacity='0';return;}
      foreground.style.opacity='0';canvas.style.opacity=amount>=1?'0':'1';
      gl.uniform1f(progress,amount);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);
    };
    const previous=timeline.eventCallback('onUpdate');timeline.eventCallback('onUpdate',()=>{previous?.();update();});
    // The master already spans the unchanged scene duration. No new time is added.
    root.dataset.exitStart=String(start);root.dataset.exitDuration=String(settings.durationSec);update();
    window.__hfForceTimelineRebind?.();return true;
  }
  window.GLDomainWarpExit={attach};
}());
