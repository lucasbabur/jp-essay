import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const bin = fileURLToPath(new URL('../bin/jp-essay.js', import.meta.url));
const run = (home, ...args) => spawnSync(process.execPath, [bin, ...args], { encoding: 'utf8', env: { ...process.env, HOME: home, USERPROFILE: home } });
const skills = home => path.join(home, '.claude', 'skills');

test('installs both skills with every file the skill reads', () => {
  const home = mkdtempSync(path.join(tmpdir(), 'jp-'));
  const r = run(home);
  assert.equal(r.status, 0, r.stderr);
  for (const f of ['SKILL.md', 'check.py', 'style.md', 'tells.md', 'assets/icon.png', 'scientific/SKILL.md'])
    statSync(path.join(skills(home), 'jp-essay', f));
  assert.ok(statSync(path.join(skills(home), 'jp-essay', 'check.py')).mode & 0o100);
  assert.match(readFileSync(path.join(skills(home), 'jp-essay-scientific', 'SKILL.md'), 'utf8'), /jp-essay-scientific/);
});

test('a second run reports up to date', () => {
  const home = mkdtempSync(path.join(tmpdir(), 'jp-'));
  run(home);
  assert.match(run(home).stdout, /up to date/);
});

test('refuses to overwrite a modified install without --force', () => {
  const home = mkdtempSync(path.join(tmpdir(), 'jp-'));
  run(home);
  writeFileSync(path.join(skills(home), 'jp-essay', 'SKILL.md'), 'edited');
  const r = run(home);
  assert.equal(r.status, 1);
  assert.match(r.stderr, /--force/);
  assert.equal(run(home, '--force').status, 0);
  assert.notEqual(readFileSync(path.join(skills(home), 'jp-essay', 'SKILL.md'), 'utf8'), 'edited');
});

test('points a git clone to git pull', () => {
  const home = mkdtempSync(path.join(tmpdir(), 'jp-'));
  mkdirSync(path.join(skills(home), 'jp-essay', '.git'), { recursive: true });
  assert.match(run(home).stderr, /git pull/);
});

test('rejects unknown arguments', () => {
  assert.equal(run(tmpdir(), '--project').status, 1);
});
