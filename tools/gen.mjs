#!/usr/bin/env node
/**
 * gen.mjs — two-model adviser→coder pipeline (Node.js / node-llama-cpp)
 *
 * GPU backend: node-llama-cpp with WebGL2 (default)
 * HTTP backend: llama-server on port 9000 (--http flag)
 *
 * Usage:
 *   node tools/gen.mjs "build a dark mode toggle"
 *   node tools/gen.mjs --edit path/to/file.html "add a search bar to the header"
 *   node tools/gen.mjs --patch path/to/file.js "replace hardcoded port 8080 with process.env.PORT"
 *   node tools/gen.mjs --http "landing page for GPU inference toolkit"
 *
 * Or import and call gen() directly:
 *   import { gen } from './tools/gen.mjs';
 *   const result = await gen('add error handling', { file: 'server.js', mode: 'edit' });
 *
 * Install: npm install  (from repo root — installs node-llama-cpp)
 *
 * Env vars (mirrors tools/config.py):
 *   KHANARY_INFER_URL      HTTP endpoint  (default: http://127.0.0.1:9000/v1/chat/completions)
 *   KHANARY_ADVISER_MODEL  Path to adviser GGUF
 *   KHANARY_CODER_MODEL    Path to coder GGUF
 */

import { readFileSync, writeFileSync } from 'fs';
import { parseArgs }                   from 'util';

// ---------------------------------------------------------------------------
// Config — mirrors tools/config.py
// ---------------------------------------------------------------------------
const INFER_URL     = process.env.KHANARY_INFER_URL     ?? 'http://127.0.0.1:9000/v1/chat/completions';
const ADVISER_MODEL = process.env.KHANARY_ADVISER_MODEL ?? String.raw`E:\models\GEMMA\gemma-3-1b-Q4_K_M.gguf`;
const CODER_MODEL   = process.env.KHANARY_CODER_MODEL   ?? String.raw`C:\Users\canna\.lmstudio\models\lmstudio-community\Qwen3-1.7B-GGUF\Qwen3-1.7B-Q8_0.gguf`;

// ---------------------------------------------------------------------------
// HTTP backend — calls llama-server on port 9000
// ---------------------------------------------------------------------------
async function httpChat(messages, maxTokens = 400, temperature = 0.2) {
    const res = await fetch(INFER_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ messages, max_tokens: maxTokens, temperature, stream: false }),
        signal:  AbortSignal.timeout(300_000),
    });
    if (!res.ok) throw new Error(`llama-server ${res.status}: ${await res.text()}`);
    const data = await res.json();
    return data.choices[0].message.content;
}

// ---------------------------------------------------------------------------
// WebGL2 backend — node-llama-cpp loaded in-process
// ---------------------------------------------------------------------------
let _llama    = null;
let _adviser  = null;
let _advCtx   = null;
let _coder    = null;
let _coderCtx = null;

async function loadModels() {
    if (_llama) return;
    let getLlama, LlamaChatSession;
    try {
        ({ getLlama, LlamaChatSession } = await import('node-llama-cpp'));
    } catch {
        console.error('[gen] node-llama-cpp not installed — run: npm install');
        process.exit(1);
    }

    process.stderr.write('[gen] initialising WebGL2 llama runtime…\n');
    _llama = await getLlama({ gpu: 'webgl' });

    process.stderr.write('[gen] loading adviser (Gemma)…\n');
    _adviser  = await _llama.loadModel({ modelPath: ADVISER_MODEL });
    _advCtx   = await _adviser.createContext({ contextSize: 2048 });

    process.stderr.write('[gen] loading coder (Qwen3)…\n');
    _coder    = await _llama.loadModel({ modelPath: CODER_MODEL });
    _coderCtx = await _coder.createContext({ contextSize: 4096 });

    process.stderr.write('[gen] models ready\n');
}

async function webglChat(model, ctx, systemPrompt, userPrompt, maxTokens, temperature) {
    const { LlamaChatSession } = await import('node-llama-cpp');
    const session = new LlamaChatSession({
        contextSequence: ctx.getSequence(),
        systemPrompt,
    });
    return session.prompt(userPrompt, { maxTokens, temperature });
}

// ---------------------------------------------------------------------------
// Core pipeline
// ---------------------------------------------------------------------------
/**
 * Two-step adviser→coder generation.
 *
 * @param {string}  prompt     Task description
 * @param {object}  [opts]
 * @param {string}  [opts.file]      Absolute path to target file (required for edit/patch)
 * @param {string}  [opts.mode]      'gen' | 'edit' | 'patch'   (default: 'gen')
 * @param {number}  [opts.maxTokens] Max tokens for coder output (default: 4096)
 * @param {string}  [opts.backend]   'webgl' | 'http'            (default: 'webgl')
 * @returns {Promise<{plan:string, code:string, written:boolean, file:string|null}>}
 */
export async function gen(prompt, {
    file      = null,
    mode      = 'gen',
    maxTokens = 4096,
    backend   = 'webgl',
} = {}) {
    if (backend === 'webgl') await loadModels();

    const chat = async (sys, user, max, temp) =>
        backend === 'http'
            ? httpChat([{ role: 'system', content: sys }, { role: 'user', content: user }], max, temp)
            : webglChat(_adviser, _advCtx, sys, user, max, temp);

    const code_ = async (sys, user, max, temp) =>
        backend === 'http'
            ? httpChat([{ role: 'system', content: sys }, { role: 'user', content: user }], max, temp)
            : webglChat(_coder, _coderCtx, sys, user, max, temp);

    // Step 1 — adviser produces a brief
    let plan = '';
    try {
        plan = await chat(
            'You are a concise implementation planner. Return 5-8 short bullets covering structure, requirements, and key decisions. No code.',
            `Create an implementation brief for:\n\n${prompt}`,
            400, 0.2,
        );
    } catch (e) {
        process.stderr.write(`[gen] adviser step failed (continuing): ${e.message}\n`);
    }

    // Step 2 — read target file for edit/patch
    let fileContent = '';
    if (file) {
        try { fileContent = readFileSync(file, 'utf8'); } catch { /* new file */ }
    }

    // Step 3 — build coder prompt
    const isFileOp = Boolean(file && (mode === 'edit' || mode === 'patch'));
    let coderPrompt = `/no_think\nTask:\n${prompt}`;
    if (plan)        coderPrompt += `\n\nImplementation brief (reference only, do not quote):\n${plan}`;
    if (fileContent) coderPrompt += `\n\nExisting file (${file}):\n\`\`\`\n${fileContent}\n\`\`\`\nReturn the complete updated file only.`;

    const systemMsg = isFileOp
        ? 'You are a precise code editor. Return the complete updated file only. No explanation, no markdown fences.'
        : 'You are a code generator. Return complete working code only. No explanation.';

    // Step 4 — coder generates
    let code = '';
    try {
        code = await code_(systemMsg, coderPrompt, maxTokens, 0.1);
        // Strip stray markdown fences if model wraps output
        if (code.startsWith('```')) {
            const lines = code.split('\n');
            code = lines.slice(1, lines.at(-1).trim() === '```' ? -1 : undefined).join('\n');
        }
    } catch (e) {
        process.stderr.write(`[gen] coder step failed: ${e.message}\n`);
    }

    // Step 5 — write back for edit/patch
    let written = false;
    if (isFileOp && code) {
        writeFileSync(file, code, 'utf8');
        written = true;
        process.stderr.write(`[gen] wrote ${file}\n`);
    }

    return { plan, code, written, file };
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
async function main() {
    const { values, positionals } = parseArgs({
        args:           process.argv.slice(2),
        allowPositionals: true,
        options: {
            edit:  { type: 'string' },
            patch: { type: 'string' },
            http:  { type: 'boolean', default: false },
        },
    });

    const prompt  = positionals.join(' ');
    const backend = values.http ? 'http' : 'webgl';

    if (!prompt) {
        console.error('Usage: node tools/gen.mjs [--edit FILE | --patch FILE] [--http] "<task>"');
        process.exit(1);
    }

    let result;
    if (values.edit)  result = await gen(prompt, { file: values.edit,  mode: 'edit',  backend });
    else if (values.patch) result = await gen(prompt, { file: values.patch, mode: 'patch', backend });
    else              result = await gen(prompt, { backend });

    console.log('\n=== PLAN ===');
    console.log(result.plan || '(none)');
    console.log('\n=== CODE ===');
    console.log(result.code || '(none)');
    if (result.written) console.log(`\n[written → ${result.file}]`);
}

main().catch(e => { console.error(e); process.exit(1); });
