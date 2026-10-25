#!/usr/bin/env node
// Copies /jp-essay and /jp-essay-scientific into ~/.claude/skills. The skills call
// ~/.claude/skills/jp-essay/check.py by that path, so the user-level location is fixed.
import { spawnSync } from 'node:child_process';
import { chmod, cp, lstat, mkdtemp, mkdir, readFile, rename, rm } from 'node:fs/promises';
import { homedir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const skillFiles = ['SKILL.md', 'check.py', 'style.md', 'tells.md', 'assets/icon.png', 'scientific/SKILL.md'];
const usage = `jp-essay: install the essay-writing skills for Claude Code

  npx jp-essay@latest           Install /jp-essay and /jp-essay-scientific into ~/.claude/skills
  npx jp-essay@latest --force   Replace an existing or modified installation
  npx jp-essay@latest doctor    Check that Claude Code and uv are installed
  jp-essay --help | --version

Requires Claude Code and uv (https://docs.astral.sh/uv/).
`;

async function existing(p) {
  try {
    return await lstat(p);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

async function sameFiles(target, files, from) {
  for (const file of files) {
    const stat = await existing(path.join(target, file));
    if (!stat?.isFile()) return false;
    if (!(await readFile(path.join(target, file))).equals(await readFile(path.join(from, file)))) return false;
  }
  return true;
}

// Stage the new copy beside the target, then swap it in, so a failed copy never leaves half a skill.
async function place(target, files, from, force) {
  const current = await existing(target);
  if (current?.isDirectory() && !current.isSymbolicLink() && await sameFiles(target, files, from)) return 'up to date';
  if (current && !force) {
    const hint = (await existing(path.join(target, '.git'))) ? ' It is a git clone: update it with git pull, or' : '';
    throw new Error(`${target} already exists and differs from this version.${hint} use --force to replace it.`);
  }
  const parent = path.dirname(target);
  await mkdir(parent, { recursive: true });
  const staging = await mkdtemp(path.join(parent, `.${path.basename(target)}-`));
  try {
    for (const file of files) await cp(path.join(from, file), path.join(staging, file), { recursive: true });
    if (files.includes('check.py')) await chmod(path.join(staging, 'check.py'), 0o755);
    if (current) await rm(target, { recursive: true, force: true });
    await rename(staging, target);
  } finally {
    await rm(staging, { recursive: true, force: true });
  }
  return 'installed';
}

async function install(force) {
  const skills = path.join(homedir(), '.claude', 'skills');
  const main = path.join(skills, 'jp-essay');
  const scientific = path.join(skills, 'jp-essay-scientific');
  console.log(`/jp-essay: ${await place(main, skillFiles, root, force)} at ${main}`);
  console.log(`/jp-essay-scientific: ${await place(scientific, ['SKILL.md'], path.join(root, 'scientific'), force)} at ${scientific}`);
  console.log(`\nStart a new Claude Code session, then run:\n  /jp-essay Why do we procrastinate on things we care about? 1200 en`);
  if (!doctor(true)) console.log('\nThe gate checker needs uv: https://docs.astral.sh/uv/');
}

function doctor(quiet = false) {
  let ok = true;
  for (const command of ['claude', 'uv']) {
    const r = spawnSync(command, ['--version'], { encoding: 'utf8', timeout: 10000, windowsHide: true, shell: process.platform === 'win32' });
    const found = !r.error && r.status === 0;
    if (!quiet) console.log(`${found ? 'OK     ' : 'MISSING'} ${command}${found ? `  ${r.stdout.trim().split('\n')[0]}` : ''}`);
    ok &&= found || (quiet && command === 'claude');
  }
  return ok;
}

try {
  const args = process.argv.slice(2);
  const unknown = args.find(a => !['--force', 'install', 'doctor', '--help', '-h', '--version', '-v'].includes(a));
  if (unknown) throw new Error(`unknown argument ${unknown}. Run jp-essay --help.`);
  if (args.includes('--help') || args.includes('-h')) console.log(usage);
  else if (args.includes('--version') || args.includes('-v')) console.log(JSON.parse(await readFile(path.join(root, 'package.json'), 'utf8')).version);
  else if (args.includes('doctor')) process.exitCode = doctor() ? 0 : 1;
  else await install(args.includes('--force'));
} catch (error) {
  console.error(`jp-essay: ${error.message}`);
  process.exitCode = 1;
}
