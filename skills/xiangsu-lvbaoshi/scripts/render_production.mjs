import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const assets=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../assets'),ctx={window:{}};
vm.createContext(ctx);
for(const name of ['base','focus','production']){vm.runInContext(fs.readFileSync(path.join(assets,name+'.js'),'utf8'),ctx);Object.assign(ctx,{GLBase:ctx.window.GLBase,GLSampleModules:ctx.window.GLSampleModules});}
const x=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(ctx.window.GLProduction.render(x.kind,x.data,x.duration,x.id));
