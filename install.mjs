import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import crypto from 'node:crypto';

const root = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
if (args.includes('--help')) {
  console.log('node install.mjs [--destination <skills-dir>] [--skills-only]\nExisting skills are never overwritten. Runtime setup needs internet.');
  process.exit(0);
}
let dest = path.join(process.env.CODEX_HOME || path.join(os.homedir(), '.codex'), 'skills');
let skillsOnly = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--skills-only') skillsOnly = true;
  else if (args[i] === '--destination' && args[i + 1] && !args[i + 1].startsWith('--')) dest = args[++i];
  else throw new Error(`Unknown or incomplete argument: ${args[i]}`);
}
const [major, minor] = process.versions.node.split('.').map(Number);
if (major < 22 || (major === 22 && minor < 14)) throw new Error('Node.js 22.14+ is required');
dest = path.resolve(dest);
const names = ['xiangsu-lvbaoshi', 'xiangsu-mg'];
const transient = name => ['node_modules', '__pycache__', '.git'].includes(name) || /\.py[co]$/.test(name);
function check(source, target) {
  if (!fs.existsSync(target)) return;
  if (fs.lstatSync(target).isSymbolicLink()) throw new Error(`Linked destination is not supported: ${target}`);
  for (const entry of fs.readdirSync(source, {withFileTypes:true})) {
    if (transient(entry.name)) continue;
    const from = path.join(source, entry.name), to = path.join(target, entry.name);
    if (!fs.existsSync(to)) throw new Error(`Incomplete existing skill preserved: ${target}`);
    if (entry.isDirectory()) { if (!fs.statSync(to).isDirectory()) throw new Error(`Conflict: ${to}`); check(from, to); }
    else {
      const hash = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
      if (!fs.statSync(to).isFile() || hash(from) !== hash(to)) throw new Error(`Existing skill differs: ${to}. Choose a new --destination.`);
    }
  }
}
for (const name of names) {
  check(path.join(root, 'skills', name), path.join(dest, name));
}
fs.mkdirSync(dest, { recursive: true });
for (const name of names) if (!fs.existsSync(path.join(dest, name))) fs.cpSync(path.join(root, 'skills', name), path.join(dest, name), { recursive: true, errorOnExist: true, force: false, filter: source => !transient(path.basename(source)) });
console.log(`Installed skills to ${dest}`);
if (!skillsOnly) {
  const runtime = await import(pathToFileURL(path.join(dest, 'xiangsu-mg', 'scripts', 'runtime.mjs')).href);
  runtime.prepareRuntime(path.join(dest, 'xiangsu-mg', 'runtime'));
  const result = spawnSync('python', ['--version'], {stdio: 'inherit', windowsHide: true});
  if (result.error || result.status !== 0) throw new Error('Skills installed; Python 3 is missing. Install Python and follow INSTALL.md.');
  console.log('Core runtime ready. Continue with INSTALL.md to install the official HyperFrames skills and Pillow.');
}
