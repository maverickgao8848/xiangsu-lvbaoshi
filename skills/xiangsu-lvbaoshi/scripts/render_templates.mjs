import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const skill=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const assets=process.argv[2]?path.resolve(process.argv[2]):path.join(skill,'assets');
const ctx={window:{}};vm.createContext(ctx);
for(const n of ['base','focus','flow','extra','material-regions','material'])vm.runInContext(fs.readFileSync(path.join(assets,`${n}.js`),'utf8'),ctx);
const entries=JSON.parse(fs.readFileSync(0,'utf8'));
console.log(JSON.stringify(entries.map(e=>{
  let body=ctx.window.GLSampleModules[e.templateId].render(e.content||{},'assets/glass-lime/');
  if(e.content?.object&&e.templateId!=='L24')body+=`<div class="gl-companion-object"><img src="${ctx.window.GLBase.esc(e.content.object)}" alt=""></div>`;
  return {id:e.id,body};
})));
