import fs from 'node:fs';import path from 'node:path';import http from 'node:http';import crypto from 'node:crypto';import {createRequire} from 'node:module';
const args=Object.fromEntries(process.argv.slice(2).reduce((rows,arg,i,all)=>arg.startsWith('--')?[...rows,[arg.slice(2),all[i+1]]]:rows,[]));
if(!args.project)throw Error('Use --project <prepared project>. Optional: --playwright-module <Node package root> --browser <Chromium executable>.');
const project=path.resolve(args.project),require=args['playwright-module']?createRequire(path.join(path.resolve(args['playwright-module']),'package.json')):createRequire(import.meta.url);
const {chromium}=require('playwright');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.ttf':'font/ttf','.woff2':'font/woff2'};
const server=http.createServer((req,res)=>{
  const file=path.resolve(project,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!file.startsWith(project+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);res.end();return;}
  res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});fs.createReadStream(file).pipe(res);
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try{
  browser=await chromium.launch({headless:true,...(args.browser?{executablePath:path.resolve(args.browser)}:{})});
  const page=await browser.newPage({viewport:{width:1920,height:1080}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const manifest=JSON.parse(fs.readFileSync(path.join(project,'verification/exit-capture/capture-manifest.json'))),out=path.join(project,'assets/glass-lime-exits');fs.mkdirSync(out,{recursive:true});
  let credits=JSON.parse(fs.readFileSync(path.join(project,'asset-credits.json')));
  for(const [id,item] of Object.entries(manifest)){
    await page.goto(`http://127.0.0.1:${server.address().port}/verification/exit-capture/${id}.html`);await page.waitForFunction(()=>window.captureReady);
    const regions=await page.evaluate(padding=>{
      const root=document.querySelector('#capture'),stage=root.getBoundingClientRect(),foreground=root.querySelector('.foreground');
      const box=r=>{const x=Math.max(0,Math.floor(r.left-stage.left)-padding),y=Math.max(0,Math.floor(r.top-stage.top)-padding);return {x,y,width:Math.min(1920,Math.ceil(r.right-stage.left)+padding)-x,height:Math.min(1080,Math.ceil(r.bottom-stage.top)+padding)-y};};
      const visible=node=>{for(let n=node;n&&n!==foreground;n=n.parentElement){const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)<.03)return false;}return true;};
      const objects=[...foreground.querySelectorAll('.gl-companion-object')].filter(visible);
      let anchors=[...foreground.querySelectorAll('.f-lexicon,.f-comment-first,.f-comment-second,.v-checklist')].filter(visible);
      if(!anchors.length){
        const rects=[...foreground.querySelectorAll('*')].filter(n=>{
          if(n.closest('.gl-companion-object')||!visible(n))return false;
          const s=getComputedStyle(n);return [...n.childNodes].some(c=>c.nodeType===3&&c.textContent.trim())||['IMG','svg'].includes(n.tagName)||s.backgroundImage!=='none'||!['transparent','rgba(0, 0, 0, 0)'].includes(s.backgroundColor)||parseFloat(s.borderTopWidth)>0;
        }).map(n=>n.getBoundingClientRect()).filter(r=>r.width&&r.height);
        if(rects.length)anchors=[{getBoundingClientRect:()=>({left:Math.min(...rects.map(r=>r.left)),top:Math.min(...rects.map(r=>r.top)),right:Math.max(...rects.map(r=>r.right)),bottom:Math.max(...rects.map(r=>r.bottom))})}];
      }
      return [...anchors,...objects].map(n=>box(n.getBoundingClientRect())).filter(b=>b.width>0&&b.height>0);
    },item.paddingPx);
    if(!regions.length||regions.length>4)throw Error('Expected 1–4 local foreground regions: '+id);
    const png=await page.screenshot({path:path.join(out,id+'.png'),omitBackground:true});
    const alpha=await page.evaluate(async encoded=>{
      const image=new Image();image.src='data:image/png;base64,'+encoded;await image.decode();const c=document.createElement('canvas');c.width=1920;c.height=1080;const ctx=c.getContext('2d');ctx.drawImage(image,0,0);
      const pixels=ctx.getImageData(0,0,1920,1080).data;let painted=0;for(let i=3;i<pixels.length;i+=4)if(pixels[i])painted++;
      return {painted,cornerAlpha:[pixels[3],pixels[1919*4+3],pixels[(1079*1920)*4+3]]};
    },png.toString('base64'));
    if(alpha.cornerAlpha.some(a=>a!==0)||alpha.painted>1920*1080*.6)throw Error('Capture contains a background; use isolated local foreground: '+id);
    const digest=crypto.createHash('sha256').update(png).digest('hex');manifest[id]={...item,regions,alpha,textureSha256:digest};
    const relative='assets/glass-lime-exits/'+id+'.png';credits=credits.filter(c=>c.path!==relative);
    credits.push({path:relative,sha256:digest,sourcePage:'generated:actual-glass-lime-foreground:'+id,sourceLabel:'Actual frozen foreground only; no host/background pixels',fingerprint:item.fingerprint});
  }
  if(errors.length)throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));fs.writeFileSync(path.join(project,'asset-credits.json'),JSON.stringify(credits,null,2));
  console.log(JSON.stringify({captures:Object.keys(manifest).length,manifest:path.join(out,'manifest.json')}));
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
