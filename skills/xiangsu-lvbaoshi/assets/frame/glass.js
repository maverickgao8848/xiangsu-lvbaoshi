(function(){
  const NS='http://www.w3.org/2000/svg',cache=new Map();
  function surfaceMaps(width,height,radius,path){
    const ratio=Math.min(1,1000/width),w=Math.max(8,Math.round(width*ratio)),h=Math.max(8,Math.round(height*ratio));
    const key=[w,h,radius,path].join('|');if(cache.has(key))return cache.get(key);
    const mask=document.createElement('canvas');mask.width=w;mask.height=h;
    const c=mask.getContext('2d');c.scale(ratio,ratio);c.fillStyle='#fff';
    if(path)c.fill(new Path2D(path));else{c.beginPath();c.roundRect(0,0,width,height,radius.map(value=>Math.min(value,width/2,height/2)));c.fill();}
    const alpha=c.getImageData(0,0,w,h).data;
    // Distance to the OUTSIDE of the silhouette, including the canvas boundary.
    // The old clamped alpha gradient became zero on straight edges; only the
    // corners refracted. Padding makes all four bevels have an actual normal.
    const stride=w+2,dist=new Float32Array(stride*(h+2));
    for(let y=0;y<h;y++)for(let x=0;x<w;x++)dist[(y+1)*stride+x+1]=alpha[(y*w+x)*4+3]>127?1e5:0;
    const diagonal=Math.SQRT2;
    for(let y=1;y<=h;y++)for(let x=1;x<=w;x++){
      const i=y*stride+x;dist[i]=Math.min(dist[i],dist[i-1]+1,dist[i-stride]+1,dist[i-stride-1]+diagonal,dist[i-stride+1]+diagonal);
    }
    for(let y=h;y>=1;y--)for(let x=w;x>=1;x--){
      const i=y*stride+x;dist[i]=Math.min(dist[i],dist[i+1]+1,dist[i+stride]+1,dist[i+stride+1]+diagonal,dist[i+stride-1]+diagonal);
    }
    const out=document.createElement('canvas');out.width=w;out.height=h;
    const o=out.getContext('2d'),pixels=o.createImageData(w,h);
    const edge=document.createElement('canvas');edge.width=w;edge.height=h;
    const ec=edge.getContext('2d'),rim=ec.createImageData(w,h);
    const bevel=15*ratio,gauss=(v,center,spread)=>Math.exp(-(((v-center)/spread)**2));
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){
      const i=(y*w+x)*4,j=(y+1)*stride+x+1,d=dist[j];
      pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=128;pixels.data[i+3]=255;
      if(d<=0||d>bevel)continue;
      const dx=(dist[j+1]-dist[j-1])/2,dy=(dist[j+stride]-dist[j-stride])/2,len=Math.hypot(dx,dy)||1;
      const nx=-dx/len,ny=-dy/len,t=Math.min(1,d/bevel);
      // Curved front bevel: grazing normals on the outside, flat in the middle.
      const slope=Math.cos(t*Math.PI/2),nz=Math.sin(t*Math.PI/2);
      const refraction=slope*Math.sin(Math.PI*t);
      pixels.data[i]=128+nx*refraction*110;pixels.data[i+1]=128+ny*refraction*110;
      const facing=Math.max(0,-nx*.48-ny*.7),back=Math.max(0,nx*.48+ny*.7);
      const spec=Math.pow(Math.max(0,-nx*slope*.28-ny*slope*.4+nz*.87),22);
      // Separate dark rear face, coloured inner reflection and white front lip.
      // Coloured patches vary along the perimeter: no uniform rainbow outline.
      const patches=.45+.55*Math.pow(Math.sin(x/w*8.5+y/h*5.1+.8),2);
      const cool=(1+Math.sin(x/w*5.8-y/h*3.7+.6))/2;
      const band=gauss(t,.3,.16)*patches*(.38+back*.36);
      const dark=gauss(t,.54,.22)*(.14+back*.35);
      const lip=gauss(t,.085,.06)*(.24+facing*.5)+spec*.38;
      const glow=gauss(t,.8,.18)*facing*.12;
      const baseAlpha=Math.min(.94,band+dark+lip+glow);
      const color=[235*(1-cool)+72*cool,169*(1-cool)+132*cool,78*(1-cool)+249*cool];
      for(let channel=0;channel<3;channel++)rim.data[i+channel]=(color[channel]*band+12*dark+244*lip+215*glow)/(baseAlpha||1);
      rim.data[i+3]=baseAlpha*alpha[i+3];
    }
    o.putImageData(pixels,0,0);ec.putImageData(rim,0,0);
    const value={normal:out.toDataURL(),edge:edge.toDataURL()};cache.set(key,value);return value;
  }
  function install(root,id){
    root.querySelector('.glass-filters')?.remove();
    const svg=document.createElementNS(NS,'svg');svg.classList.add('glass-filters');svg.setAttribute('width','0');svg.setAttribute('height','0');svg.style.position='absolute';
    const defs=document.createElementNS(NS,'defs');svg.append(defs);root.prepend(svg);
    root.querySelectorAll('.glass').forEach((plate,index)=>{
      const width=plate.offsetWidth,height=plate.offsetHeight,style=getComputedStyle(plate);
      const radius=['borderTopLeftRadius','borderTopRightRadius','borderBottomRightRadius','borderBottomLeftRadius'].map(key=>parseFloat(style[key])||0);
      const fid=`${id}-lens-${index}`,maps=surfaceMaps(width,height,radius,plate.dataset.glassPath);
      const filter=document.createElementNS(NS,'filter');filter.id=fid;
      filter.setAttribute('filterUnits','userSpaceOnUse');filter.setAttribute('primitiveUnits','userSpaceOnUse');
      filter.setAttribute('x','0');filter.setAttribute('y','0');filter.setAttribute('width',String(width));filter.setAttribute('height',String(height));filter.setAttribute('color-interpolation-filters','sRGB');
      // Explicit local pixels prevent the backdrop's viewport-sized filter
      // region from spreading edge dispersion across the clear centre.
      filter.innerHTML=`<feImage href="${maps.normal}" x="0" y="0" width="${width}" height="${height}" preserveAspectRatio="none" result="normal"/>
        <feDisplacementMap in="SourceGraphic" in2="normal" scale="46" xChannelSelector="R" yChannelSelector="G" result="r"/>
        <feColorMatrix in="r" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="red"/>
        <feDisplacementMap in="SourceGraphic" in2="normal" scale="36" xChannelSelector="R" yChannelSelector="G" result="g"/>
        <feColorMatrix in="g" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="green"/>
        <feDisplacementMap in="SourceGraphic" in2="normal" scale="26" xChannelSelector="R" yChannelSelector="G" result="b"/>
        <feColorMatrix in="b" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="blue"/>
        <feBlend in="red" in2="green" mode="screen" result="rg"/><feBlend in="rg" in2="blue" mode="screen" result="rgb"/>
        <feGaussianBlur in="rgb" stdDeviation=".35"/>`;
      defs.append(filter);
      // Filter the actual backdrop. A copied host image drifts as the plate moves
      // and incorrectly inserts a person over a grid or a new destination.
      plate.style.setProperty('--glass-optics',`url(#${fid})`);
      plate.style.setProperty('--glass-edge',`url("${maps.edge}")`);
    });
  }
  window.GLGlass={install};
}());
