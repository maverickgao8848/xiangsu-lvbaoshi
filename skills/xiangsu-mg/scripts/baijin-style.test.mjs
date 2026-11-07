import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { inheritFrame, verifyInheritedFrame } from './inherit-frame.mjs';

const skill=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
async function isolated(t){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'baijin-style-'));
  t.after(()=>{assert.equal(path.dirname(root),fs.realpathSync(os.tmpdir()));assert.ok(path.basename(root).startsWith('baijin-style-'));fs.rmSync(root,{recursive:true,force:true});});
  const installed=path.join(root,'skills/xiangsu-mg');
  fs.mkdirSync(path.join(installed,'scripts'),{recursive:true});
  fs.copyFileSync(path.join(skill,'scripts/apply-style.mjs'),path.join(installed,'scripts/apply-style.mjs'));
  fs.cpSync(path.join(skill,'assets/styles/baijin-black-texture'),path.join(installed,'assets/styles/baijin-black-texture'),{recursive:true});
  const {applyStyle}=await import(pathToFileURL(path.join(installed,'scripts/apply-style.mjs')).href);
  return {root,installed,applyStyle};
}
test('Baijin is complete in an MG-only installation and preserves conflicting user resources',async t=>{
  const {root,applyStyle}=await isolated(t),projectDirectory=path.join(root,'film');
  assert.equal(applyStyle({styleId:'baijin-black-texture',projectDirectory}).status,'applied');
  const pack=path.join(projectDirectory,'assets/references/styles/baijin-black-texture');
  const record=JSON.parse(fs.readFileSync(path.join(projectDirectory,'frame-resources.json')));
  assert.equal(record.styleId,'baijin-black-texture');
  for(const item of record.resources)assert.equal(hash(fs.readFileSync(path.join(projectDirectory,item.path))),item.sha256);
  for(const relative of ['runtime/black-texture.css','runtime/theme.css']){
    const css=path.join(pack,relative);
    for(const match of fs.readFileSync(css,'utf8').matchAll(/url\(['"]?([^)'"\s]+)['"]?\)/g)){
      const target=path.resolve(path.dirname(css),decodeURIComponent(match[1]));
      assert.ok(target.startsWith(projectDirectory+path.sep));assert.ok(fs.statSync(target).size>0);
    }
  }
  assert.equal(applyStyle({styleId:'baijin-black-texture',projectDirectory}).status,'unchanged');
  const file=path.join(pack,'runtime/theme.css'),frame=fs.readFileSync(path.join(projectDirectory,'frame.md'));
  fs.writeFileSync(file,'user-owned change');
  assert.throws(()=>applyStyle({styleId:'baijin-black-texture',projectDirectory}),/differs/);
  assert.equal(fs.readFileSync(file,'utf8'),'user-owned change');
  assert.deepEqual(fs.readFileSync(path.join(projectDirectory,'frame.md')),frame);
});
test('Baijin frame and resources survive source Skill removal and parent relocation',async t=>{
  const {root,installed,applyStyle}=await isolated(t),project=path.join(root,'film');
  applyStyle({styleId:'baijin-black-texture',projectDirectory:project});
  fs.renameSync(installed,path.join(root,'detached-installation'));
  const child=path.join(project,'animations/mechanism');
  assert.equal(inheritFrame({projectDirectory:child,upstream:project}).styleId,'baijin-black-texture');
  assert.equal(verifyInheritedFrame(child).ok,true);
  const moved=path.join(root,'relocated');fs.renameSync(project,moved);
  const current=path.join(moved,'animations/mechanism');
  assert.equal(verifyInheritedFrame(current).ok,true);
  const grandchild=path.join(current,'animations/detail');
  inheritFrame({projectDirectory:grandchild,upstream:current});
  assert.equal(verifyInheritedFrame(grandchild).ok,true);
  assert.equal(fs.readFileSync(path.join(grandchild,'frame.md'),'utf8'),fs.readFileSync(path.join(current,'frame.md'),'utf8'));
});
test('Baijin rejects unknown options or corrupted resources before creating a project',async t=>{
  const {root,installed,applyStyle}=await isolated(t),projectDirectory=path.join(root,'film');
  assert.throws(()=>applyStyle({styleId:'baijin-black-texture',projectDirectory,unsupportedOption:true}),/Unknown style option/);
  assert.equal(fs.existsSync(projectDirectory),false);
  fs.writeFileSync(path.join(installed,'assets/styles/baijin-black-texture/runtime/black-texture.js'),'corrupt');
  assert.throws(()=>applyStyle({styleId:'baijin-black-texture',projectDirectory}),/hash mismatch/);
  assert.equal(fs.existsSync(projectDirectory),false);
});
