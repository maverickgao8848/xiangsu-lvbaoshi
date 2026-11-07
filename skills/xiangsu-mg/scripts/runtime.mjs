import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

export const runtimeDirectory=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../runtime');
export function runtimeRequire(root=runtimeDirectory){return createRequire(path.join(root,'package.json'));}
export function runtimeEnvironment(root=runtimeDirectory){
  const require=runtimeRequire(root);
  const directories=[path.dirname(require('ffmpeg-static')),path.dirname(require('ffprobe-static').path)];
  return {...process.env,PATH:[...directories,process.env.PATH??''].join(path.delimiter)};
}
export function npmInstall(root=runtimeDirectory){
  const npmCli=path.join(path.dirname(process.execPath),'node_modules/npm/bin/npm-cli.js');
  const args=['ci','--no-audit','--no-fund'];
  for(let attempt=0;attempt<2;attempt++){
    const execution=fs.existsSync(npmCli)
      ?spawnSync(process.execPath,[npmCli,...args],{cwd:root,stdio:'inherit',windowsHide:true})
      :spawnSync(process.platform==='win32'?'npm.cmd':'npm',args,{cwd:root,stdio:'inherit',windowsHide:true,shell:process.platform==='win32'});
    if(!execution.error && execution.status===0)return;
    if(attempt===1)throw new Error('Runtime dependency installation failed: '+(execution.error?.message??execution.status)+'. Check the network and rerun install.mjs.');
    console.log('Runtime download was interrupted; retrying once.');
  }
}
export function ensureFfmpeg(root=runtimeDirectory){
  const require=runtimeRequire(root),binary=require('ffmpeg-static');
  const probe=()=>spawnSync(binary,['-version'],{encoding:'utf8',windowsHide:true});
  if(probe().status===0)return;
  // An interrupted upstream postinstall can leave a truncated executable behind.
  // Remove only this package's binary and retry its own platform-aware installer once.
  const packageRoot=path.dirname(require.resolve('ffmpeg-static/package.json'));
  if(path.dirname(binary)!==packageRoot)throw new Error('Unexpected FFmpeg binary location');
  console.log('The downloaded FFmpeg is unusable; downloading it again once.');
  if(fs.existsSync(binary))fs.unlinkSync(binary);
  const repair=spawnSync(process.execPath,[path.join(packageRoot,'install.js')],{cwd:packageRoot,stdio:'inherit',windowsHide:true});
  if(repair.error || repair.status!==0 || probe().status!==0)throw new Error('FFmpeg download/verification failed. Check the network and rerun install.mjs.');
}
export function runHyperframes(args,{root=runtimeDirectory,capture=false}={}){
  const cli=path.join(root,'node_modules/hyperframes/bin/hyperframes.mjs');
  if(!fs.existsSync(cli))throw new Error('Run the bundle install.mjs first to prepare HyperFrames.');
  return spawnSync(process.execPath,[cli,...args],{env:runtimeEnvironment(root),encoding:'utf8',stdio:capture?'pipe':'inherit',windowsHide:true});
}
export function prepareRuntime(root=runtimeDirectory){
  npmInstall(root);ensureFfmpeg(root);
  for(const args of [['--help'],['browser','ensure'],['doctor','--json']]){
    console.log('Preparing bundled HyperFrames: '+args.join(' '));
    const execution=runHyperframes(args,{root,capture:true});
    if(execution.error || execution.status!==0)throw new Error('HyperFrames '+args.join(' ')+' failed: '+(execution.error?.message??execution.stderr??execution.status));
    if(args[0]==='doctor'){
      const doctor=JSON.parse(execution.stdout.trim());
      const required=['Node.js','FFmpeg','FFprobe','Chrome'];
      const missing=required.filter(name=>doctor.checks?.find(check=>check.name===name)?.ok!==true);
      if(missing.length)throw new Error('Required runtime checks failed: '+missing.join(', '));
      console.log('Required runtime checks passed: '+required.join(', '));
    }
  }
}
