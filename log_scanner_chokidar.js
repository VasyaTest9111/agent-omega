#!/usr/bin/env node
/**
 * Log scanner using chokidar for immediate watching (ABSOLUTE_BRIDGE).
 *
 * Usage:
 *  node log_scanner_chokidar.js --config=./log_scanner_config.json
 *
 * Notes:
 * - Requires: npm install chokidar
 * - Runs entirely locally (no network calls).
 */
const fs = require('fs');
const fsp = fs.promises;
const path = require('path');
let chokidar;
try {
  chokidar = require('chokidar');
} catch (e) {
  console.error('Missing dependency "chokidar". Run: npm install chokidar');
  process.exit(1);
}

const ARGS = process.argv.slice(2);
function argValue(name, def) {
  const m = ARGS.find(a => a.startsWith(name + '='));
  return m ? m.split('=')[1] : def;
}
const configPath = argValue('--config', path.join(process.cwd(), 'log_scanner_config.json'));

function now() { return new Date().toISOString(); }
function log(msg) { console.log(`[${now()}] ${msg}`); }

async function loadConfig(p) {
  try {
    const raw = await fsp.readFile(p, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    throw new Error(`Cannot read config ${p}: ${e.message}`);
  }
}

// Masking helpers
function maskValue(value) {
  if (typeof value !== 'string') return value;
  value = value.replace(/([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/g, '****@****.***');
  if (value.length > 40) return value.slice(0,6) + '****' + value.slice(-6);
  if (/^[A-Za-z0-9_\-]{8,}$/.test(value)) return '****';
  return value;
}

function maskObject(obj, maskKeys) {
  if (Array.isArray(obj)) return obj.map(v => maskObject(v, maskKeys));
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      const lower = k.toLowerCase();
      const should = maskKeys.some(kw => lower === kw || lower.includes(kw));
      if (should) { out[k] = '****'; continue; }
      if (typeof v === 'string') out[k] = maskValue(v);
      else out[k] = maskObject(v, maskKeys);
    }
    return out;
  }
  return obj;
}

async function ensureDir(dir) { try { await fsp.mkdir(dir, { recursive: true }); } catch(e){} }

(async () => {
  let cfg;
  try {
    cfg = await loadConfig(configPath);
  } catch (e) {
    console.error(e.message);
    process.exit(1);
  }

  cfg.log_dir = path.resolve(cfg.log_dir || './logs');
  cfg.ext = cfg.ext || '.log';
  cfg.output_dir = path.resolve(cfg.output_dir || './log_scanner_output');
  cfg.mask_keys = Array.isArray(cfg.mask_keys) ? cfg.mask_keys : ['password','token','secret','key','apikey','accessToken'];
  cfg.read_existing = !!cfg.read_existing;
  cfg.aggregate_interval_ms = cfg.aggregate_interval_ms || 60_000;
  cfg.dry_run = !!cfg.dry_run;

  await ensureDir(cfg.output_dir);

  const positionsPath = path.join(cfg.output_dir, 'positions.json');
  let positions = {};
  try {
    const s = await fsp.readFile(positionsPath, 'utf8');
    positions = JSON.parse(s);
  } catch (e) {
    positions = {};
  }

  // In-memory aggregated events buffer
  const aggregated = [];

  // Read new bytes from file from last position; handle truncation/rotation
  async function readFromFile(filePath) {
    try {
      const stat = await fsp.stat(filePath);
      const size = stat.size;
      const last = positions[filePath] ?? (cfg.read_existing ? 0 : size);
      if (size < last) {
        // truncated (rotated) -> start from 0
        positions[filePath] = 0;
      }
      const start = positions[filePath] ?? (cfg.read_existing ? 0 : size);
      if (size > start) {
        const stream = fs.createReadStream(filePath, { start, end: size - 1, encoding: 'utf8' });
        let buf = '';
        for await (const chunk of stream) buf += chunk;
        const lines = buf.split(/\r?\n/).filter(Boolean);
        for (const line of lines) {
          let ev = { raw: line, timestamp: now(), source: path.relative(cfg.log_dir, filePath) };
          try {
            const parsed = JSON.parse(line);
            const masked = maskObject(parsed, cfg.mask_keys);
            ev.parsed = masked;
            ev.level = parsed.level || parsed.severity || parsed.lvl || null;
            ev.operator = parsed.operator || parsed.user || parsed.actor || null;
            ev.message = parsed.message || parsed.msg || null;
          } catch (e) {
            const m = line.match(/\b(operator|user|actor)[:=]\s*([A-Za-z0-9_\-@.]+)/i);
            ev.operator = m ? m[2] : null;
            ev.message = line;
          }
          aggregated.push(ev);
        }
        positions[filePath] = size;
      }
    } catch (e) {
      // ignore transient errors (file removed, locked, etc.)
    }
  }

  // Flush aggregated events to a JSONL file periodically
  let flushTimer = null;
  async function flushBuffer() {
    if (!aggregated.length) return;
    const outPath = path.join(cfg.output_dir, `events_${new Date().toISOString().replace(/[:.]/g,'-')}.jsonl`);
    const lines = aggregated.splice(0, aggregated.length).map(e => JSON.stringify(e));
    if (cfg.dry_run) {
      log(`[dry-run] Would write ${lines.length} events to ${outPath}`);
    } else {
      try {
        await fsp.appendFile(outPath, lines.join('\n') + '\n', 'utf8');
        log(`Wrote ${lines.length} events to ${outPath}`);
      } catch (e) {
        log(`Error writing events: ${e.message}`);
      }
    }
    // persist positions
    try { await fsp.writeFile(positionsPath, JSON.stringify(positions, null, 2), 'utf8'); } catch (e) {}
  }

  flushTimer = setInterval(flushBuffer, cfg.aggregate_interval_ms);

  // Setup chokidar watcher
  const watchPattern = path.join(cfg.log_dir, `**/*${cfg.ext}`);
  const watcher = chokidar.watch(watchPattern, {
    persistent: true,
    ignoreInitial: false,
    awaitWriteFinish: { stabilityThreshold: 200, pollInterval: 100 }
  });

  watcher.on('add', async (filePath) => {
    try {
      const stat = await fsp.stat(filePath);
      positions[filePath] = cfg.read_existing ? 0 : stat.size;
      log(`File added: ${path.relative(cfg.log_dir, filePath)} (pos=${positions[filePath]})`);
      if (cfg.read_existing) await readFromFile(filePath);
    } catch (e) { /* ignore */ }
  });

  watcher.on('change', async (filePath) => {
    await readFromFile(filePath);
  });

  watcher.on('unlink', async (filePath) => {
    if (positions[filePath] !== undefined) {
      log(`File removed: ${path.relative(cfg.log_dir, filePath)}`);
      delete positions[filePath];
      try { await fsp.writeFile(positionsPath, JSON.stringify(positions, null, 2), 'utf8'); } catch (e) {}
    }
  });

  watcher.on('error', (err) => {
    log(`Watcher error: ${err}`);
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    log('Shutting down: final flush');
    clearInterval(flushTimer);
    watcher.close();
    await flushBuffer();
    try { await fsp.writeFile(positionsPath, JSON.stringify(positions, null, 2), 'utf8'); } catch (e) {}
    log('Stopped');
    process.exit(0);
  });

  log(`Chokidar watcher started. dir=${cfg.log_dir}, ext=${cfg.ext}, dry_run=${cfg.dry_run}`);
})();
