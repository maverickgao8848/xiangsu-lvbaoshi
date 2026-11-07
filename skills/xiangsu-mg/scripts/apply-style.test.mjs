import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { applyStyle } from './apply-style.mjs';
import { inheritFrame, verifyInheritedFrame } from './inherit-frame.mjs';

const skill = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'xiangsu-lime-'));
  t.after(() => {
    assert.equal(path.dirname(root), fs.realpathSync(os.tmpdir()));
    assert.ok(path.basename(root).startsWith('xiangsu-lime-'));
    fs.rmSync(root, { recursive: true, force: true });
  });
  return root;
}
async function isolated(t) {
  const root = fixture(t), installed = path.join(root, 'skills/xiangsu-mg');
  fs.mkdirSync(path.join(installed, 'scripts'), { recursive: true });
  fs.copyFileSync(path.join(skill, 'scripts/apply-style.mjs'), path.join(installed, 'scripts/apply-style.mjs'));
  fs.cpSync(path.join(skill, 'assets/styles/glass-lime'), path.join(installed, 'assets/styles/glass-lime'), { recursive: true });
  const module = await import(pathToFileURL(path.join(installed, 'scripts/apply-style.mjs')).href);
  return { root, installed, apply: module.applyStyle };
}
test('Lime applies from an isolated MG-only installation, stages complete resources and is idempotent', async t => {
  const { root, apply } = await isolated(t), project = path.join(root, 'film');
  const result = apply({ styleId: 'glass-lime', projectDirectory: project });
  assert.equal(result.status, 'applied');
  const manifest = JSON.parse(fs.readFileSync(path.join(project, 'frame-resources.json')));
  assert.equal(manifest.styleId, 'glass-lime');
  for (const item of manifest.resources) {
    assert.ok(!item.path.includes('..'));
    assert.equal(digest(fs.readFileSync(path.join(project, item.path))), item.sha256);
  }
  const base = path.join(project, 'assets/references/styles/glass-lime');
  const css = fs.readFileSync(path.join(base, 'runtime/mg-style.css'), 'utf8');
  for (const match of css.matchAll(/url\(['"]?([^)'"\s]+)['"]?\)/g)) {
    const target = path.resolve(base, 'runtime', match[1]);
    assert.ok(target.startsWith(project + path.sep));
    assert.ok(fs.statSync(target).size > 0);
  }
  assert.ok(fs.statSync(path.join(base, 'runtime/glass.js')).size > 0);
  assert.equal(fs.readdirSync(path.join(base, 'samples')).length, 8);
  assert.equal(apply({ styleId: 'glass-lime', projectDirectory: project }).status, 'unchanged');
  const before = fs.readFileSync(path.join(project, 'frame.md'));
  fs.writeFileSync(path.join(base, 'runtime/glass.js'), 'user change');
  assert.throws(() => apply({ styleId: 'glass-lime', projectDirectory: project }), /differs/);
  assert.deepEqual(fs.readFileSync(path.join(project, 'frame.md')), before);
  assert.equal(fs.readFileSync(path.join(base, 'runtime/glass.js'), 'utf8'), 'user change');
});
test('Lime children and relocated copies remain complete without access to the installed pack', async t => {
  const { root, installed, apply } = await isolated(t), parent = path.join(root, 'film');
  apply({ styleId: 'glass-lime', projectDirectory: parent });
  fs.renameSync(installed, path.join(root, 'unavailable-skill'));
  const child = path.join(parent, 'animations/beat');
  const result = inheritFrame({ projectDirectory: child, upstream: parent });
  assert.equal(result.styleId, 'glass-lime');
  assert.ok(result.resourceCount >= 20);
  assert.deepEqual(fs.readFileSync(path.join(child, 'frame.md')), fs.readFileSync(path.join(parent, 'frame.md')));
  assert.equal(verifyInheritedFrame(child).ok, true);
  const moved = path.join(root, 'relocated-film');
  fs.renameSync(parent, moved);
  const relocatedChild = path.join(moved, 'animations/beat');
  assert.equal(verifyInheritedFrame(relocatedChild).ok, true);
  const grandchild = path.join(relocatedChild, 'animations/detail');
  inheritFrame({ projectDirectory: grandchild, upstream: relocatedChild });
  assert.equal(verifyInheritedFrame(grandchild).ok, true);
});
test('unknown option, corrupt asset and invalid portable dependency fail before project writes', async t => {
  const { root, installed, apply } = await isolated(t), project = path.join(root, 'film');
  assert.throws(() => apply({ styleId: 'glass-lime', projectDirectory: project, unsupportedOption: true }), /Unknown style option/);
  assert.equal(fs.existsSync(project), false);
  const pack = path.join(installed, 'assets/styles/glass-lime');
  const runtime = path.join(pack, 'runtime/glass.js'), original = fs.readFileSync(runtime);
  fs.writeFileSync(runtime, 'corrupt');
  assert.throws(() => apply({ styleId: 'glass-lime', projectDirectory: project }), /hash mismatch/);
  assert.equal(fs.existsSync(project), false);
  fs.writeFileSync(runtime, original);
  const metadataPath = path.join(pack, 'metadata.json'), metadata = JSON.parse(fs.readFileSync(metadataPath));
  metadata.frameResources.push('runtime/missing.js');
  fs.writeFileSync(metadataPath, JSON.stringify(metadata));
  assert.throws(() => apply({ styleId: 'glass-lime', projectDirectory: project }), /not selected/);
  assert.equal(fs.existsSync(project), false);
});
test('all installed styles stage one complete resource set and remain idempotent', t => {
  const root = fixture(t);
  for (const styleId of fs.readdirSync(path.join(skill, 'assets/styles'))) {
      const metadata = JSON.parse(fs.readFileSync(path.join(skill, 'assets/styles', styleId, 'metadata.json')));
      const projectDirectory = path.join(root, styleId);
      assert.equal(applyStyle({ styleId, projectDirectory }).status, 'applied');
      assert.equal(applyStyle({ styleId, projectDirectory }).status, 'unchanged');
      for (const item of metadata.files) {
        if (item.path === 'FRAME.md') continue; // A typography variant may resolve this file.
        assert.equal(digest(fs.readFileSync(path.join(projectDirectory, 'assets/references/styles', styleId, item.path))), item.sha256);
      }
      assert.equal(fs.existsSync(path.join(projectDirectory, 'frame-resources.json')), Boolean(metadata.frameResources));
    }
});
test('CLI rejects unknown switches before writing any project', t => {
  const root = fixture(t), project = path.join(root, 'film');
  const result = spawnSync(process.execPath, [path.join(skill, 'scripts/apply-style.mjs'), '--style', 'glass-lime', '--project', project, '--unsupported', 'value'], { encoding: 'utf8' });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Usage:/);
  assert.equal(fs.existsSync(project), false);
});
