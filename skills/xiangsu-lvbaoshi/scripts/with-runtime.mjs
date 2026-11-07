import path from 'node:path';
import os from 'node:os';
import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {fileURLToPath} from 'node:url';

const skills = process.env.CODEX_HOME ? path.join(process.env.CODEX_HOME, 'skills') : path.join(os.homedir(), '.codex', 'skills');
const sibling = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'xiangsu-mg');
const mg = process.env.XIANGSU_MG_DIR || (fs.existsSync(sibling) ? sibling : path.join(skills, 'xiangsu-mg'));
const runtime = path.join(mg, 'scripts', 'runtime.mjs');
if (!fs.existsSync(runtime)) throw new Error('Set XIANGSU_MG_DIR to the installed xiangsu-mg directory.');
const {runtimeEnvironment} = await import(pathToFileURL(runtime).href);
const [command, ...args] = process.argv.slice(2);
if (!command) throw new Error('Usage: node with-runtime.mjs <command> [arguments...]');
const result = spawnSync(command, args, {env: runtimeEnvironment(), stdio:'inherit', windowsHide:true});
if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
