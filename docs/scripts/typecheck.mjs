import { execFileSync } from 'node:child_process';
import { statSync } from 'node:fs';

const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const serverEntry = new URL('../.source/server.ts', import.meta.url);

for (let attempt = 1; attempt <= 5; attempt += 1) {
  execFileSync(npx, ['next', 'typegen'], { stdio: 'inherit' });

  try {
    if (statSync(serverEntry).size > 0) break;
  } catch {
    // Fumadocs may still be creating its generated entry on the first pass.
  }

  if (attempt === 5) {
    throw new Error('Fumadocs did not generate .source/server.ts');
  }
}

execFileSync(npx, ['tsc', '--noEmit'], { stdio: 'inherit' });
