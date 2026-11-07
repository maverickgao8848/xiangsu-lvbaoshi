import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const skill=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=Object.fromEntries(process.argv.slice(2).reduce((items,value,index,list)=>value.startsWith('--')?[...items,[value.slice(2),list[index+1]]]:items,[]));
if(!args.out)throw new Error('Provide --out <new preview directory>.');
const out=path.resolve(args.out);
if(fs.existsSync(out)&&fs.readdirSync(out).length)throw new Error('Preview output must be a new or empty directory.');
const catalog=JSON.parse(fs.readFileSync(path.join(skill,'references/effect-catalog.json'),'utf8'));
const item=catalog.find(item=>item.id===(args.effect||'L07'));if(!item)throw new Error('Unknown effect.');
const motion=args.motion||'none',sound=args.sound||'auto';
const config=JSON.parse(fs.readFileSync(path.join(skill,'references/motion.json'),'utf8'));
if(motion!=='none'&&!config.variants.some(variant=>variant.id===motion))throw new Error('Unknown motion.');
if(item.id==='L30'&&motion!=='none')throw new Error('L30 uses its own handoff.');
if(!['auto','electronic','camera','mute'].includes(sound))throw new Error('Unknown sound kit.');
const content=args.content?JSON.parse(fs.readFileSync(path.resolve(args.content),'utf8')):{};
if(args['host-finish']!==undefined){
  if(!['off','soft-edge-v1'].includes(args['host-finish']))throw new Error('Use --host-finish off|soft-edge-v1.');
  content.hostFinish={enabled:args['host-finish']!=='off',preset:'soft-edge-v1'};
}
const hostFinish=content.hostFinish||{enabled:false};
if(typeof hostFinish.enabled!=='boolean'||(hostFinish.preset!==undefined&&hostFinish.preset!=='soft-edge-v1'))throw new Error('Invalid hostFinish.');
if(hostFinish.enabled){
  const bundle=path.join(skill,'assets/host-edge-shadow');
  const preset=JSON.parse(fs.readFileSync(path.join(bundle,'preset.json'),'utf8'));
  if(crypto.createHash('sha256').update(fs.readFileSync(path.join(bundle,'soft-edge-v1.png'))).digest('hex')!==preset.assetSha256)throw new Error('Host edge shadow asset drift.');
}
const ctx={window:{}};vm.createContext(ctx);
for(const name of ['base','focus','flow','extra','material-regions','material'])vm.runInContext(fs.readFileSync(path.join(skill,`assets/${name}.js`),'utf8'),ctx);
const body=ctx.window.GLSampleModules[item.id].render(content,'assets/');
function copyDirectory(source,destination){
  fs.mkdirSync(destination,{recursive:true});
  for(const entry of fs.readdirSync(source,{withFileTypes:true})){
    const from=path.join(source,entry.name),to=path.join(destination,entry.name);
    if(entry.isDirectory())copyDirectory(from,to);
    else if(entry.isFile())fs.copyFileSync(from,to);
    else throw new Error('Library assets must be regular files or directories.');
  }
}
fs.mkdirSync(out,{recursive:true});copyDirectory(path.join(skill,'assets'),path.join(out,'assets'));
if(args.host){const source=path.resolve(args.host);if(!fs.existsSync(source))throw new Error('Host image missing.');fs.copyFileSync(source,path.join(out,'assets/host-input'+path.extname(source)));}
const host=args.host?'assets/host-input'+path.extname(args.host):'assets/host.jpg';
const css=['common','focus','flow','extra','material','envelope'].map(name=>fs.readFileSync(path.join(skill,`assets/${name}.css`),'utf8')).join('\n').replace(/\.sample-root/g,'#root').replace(/\.fine /g,'#root.fine ').replace('color:#d9d9d9;text-shadow','color:#dddeda;text-shadow');
const fonts=['GLSans:noto','GLNumbers:montserrat','GLCaption:oppo'].map(pair=>{const [family,file]=pair.split(':');return `@font-face{font-family:${family};src:url('assets/fonts/${file}.ttf');font-weight:100 900}`;}).join('');
const js=['gsap.min','base','focus','flow','extra','material-regions','material','glass','envelope','runtime'].map(name=>`<script src="assets/${name}.js"></script>`).join('');
const variant=config.variants.find(item=>item.id===motion),kit=sound==='auto'?variant?.kit:sound;
const cues=variant&&kit!=='mute'?config.cues[motion][kit]:[];
const audio=cues.map((cue,index)=>`<audio id="cue-${index}" src="${cue.file}" data-start="${cue.at}" data-duration="${config.sfxDuration[cue.file]}" data-volume="${cue.volume*config.masterVolume}" data-track-index="${30+index}"></audio>`).join('');
const data=JSON.stringify({...content,signature:motion}).replace(/</g,'\\u003c');
const page=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>${item.id} 模板样本</title><style>${fonts}${css}#root{width:100%;height:100%}</style>${js}</head><body><div id="root" class="sample-root" data-composition-id="${item.id}" data-width="1920" data-height="1080" data-duration="6" data-fps="30" style="--host-image:url('${host}')"><div class="background ${item.bg}"></div><div class="foreground clip" id="foreground" data-start="0" data-duration="6" data-track-index="2">${body}</div><div class="sample-meta"><em>${item.id}</em><span>模板样本</span></div><div class="mav-subtitle">示例画面 · 替换素材后再次核对。</div>${audio}</div><script>document.fonts.ready.then(()=>{window.__timelines=window.__timelines||{};window.__timelines['${item.id}']=GLRuntime.mount(document.getElementById('root'),'${item.id}',${data});});</script></body></html>`;
fs.writeFileSync(path.join(out,'index.html'),page);
fs.writeFileSync(path.join(out,'package.json'),JSON.stringify({name:'glass-lime-preview',private:true,scripts:{check:'npx --yes hyperframes@0.8.157 check',dev:'npx --yes hyperframes@0.8.157 preview'}},null,2));
fs.copyFileSync(path.join(skill,'asset-credits.json'),path.join(out,'asset-credits.json'));
fs.writeFileSync(path.join(out,'preview-input.json'),JSON.stringify({effect:item.id,motion,sound,content,scope:'six-second visual template example'},null,2));
console.log(JSON.stringify({out,effect:item.id,motion,sound}));
