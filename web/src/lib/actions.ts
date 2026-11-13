// Acting from the Studio app. The site is public and has no server, so to DO something (start a video, approve,
// move a card) the owner connects GitHub once on their device: a fine-grained token for THIS repository only, with
// "Actions: read and write" and "Issues: read and write" (never Contents, never anything else). It is kept in this
// browser only (localStorage), sent only to api.github.com, and can be forgotten from Settings at any time.
// Every write to files or to Notion goes through a workflow that checks the request first (studio-action.yml).

import { DEFAULTS } from './github-data.js';

const KEY = 'candela:gh-token';
const API = 'https://api.github.com';
const REPO = `${DEFAULTS.owner}/${DEFAULTS.repo}`;

export function getToken(): string {
  try { return localStorage.getItem(KEY) || ''; } catch { return ''; }
}
export function setToken(t: string) {
  try { localStorage.setItem(KEY, t.trim()); } catch { /* private mode: lasts this visit only */ memToken = t.trim(); }
}
export function forgetToken() {
  try { localStorage.removeItem(KEY); } catch { /* ignore */ }
  memToken = '';
}
let memToken = '';
const token = () => getToken() || memToken;

export class ActionError extends Error {
  constructor(public kind: 'no-token' | 'forbidden' | 'bad-token' | 'network' | 'github', message: string) { super(message); }
}

async function gh(path: string, init: RequestInit = {}) {
  const t = token();
  if (!t) throw new ActionError('no-token', 'Connect GitHub in Settings to do this from here.');
  let r: Response;
  try {
    r = await fetch(path.startsWith('http') ? path : `${API}${path}`, {
      ...init,
      headers: { Accept: 'application/vnd.github+json', Authorization: `Bearer ${t}`, 'X-GitHub-Api-Version': '2022-11-28',
                 ...(init.body ? { 'Content-Type': 'application/json' } : {}), ...(init.headers || {}) },
    });
  } catch {
    throw new ActionError('network', 'Could not reach GitHub. Check your internet and try again.');
  }
  if (r.status === 401) throw new ActionError('bad-token', 'GitHub did not accept the token (expired or wrong). Connect again in Settings.');
  if (r.status === 403 || r.status === 404) {
    const msg = await r.text().catch(() => '');
    throw new ActionError('forbidden', /rate limit/i.test(msg) ? 'GitHub limit reached; try again in a few minutes.'
      : 'The token is not allowed to do this. It needs "Actions" and "Issues" set to read and write for this repository.');
  }
  if (!r.ok) throw new ActionError('github', `GitHub answered ${r.status}: ${(await r.text().catch(() => '')).slice(0, 160)}`);
  return r.status === 204 ? null : r.json();
}

export interface Connection { login: string; canAct: boolean; expires?: string | null }

/** Check the token: who it belongs to, and whether it may start workflows in this repository. */
export async function checkConnection(): Promise<Connection> {
  const t = token();
  if (!t) throw new ActionError('no-token', 'No token on this device.');
  const r = await fetch(`${API}/user`, { headers: { Authorization: `Bearer ${t}`, Accept: 'application/vnd.github+json' } }).catch(() => null);
  if (!r) throw new ActionError('network', 'Could not reach GitHub.');
  if (r.status === 401) throw new ActionError('bad-token', 'GitHub did not accept this token.');
  const user = r.ok ? await r.json() : { login: '' };
  const expires = r.headers.get('github-authentication-token-expiration');
  let canAct = false;
  try { await gh(`/repos/${REPO}/actions/workflows?per_page=1`); canAct = true; } catch { canAct = false; }
  return { login: user.login || '', canAct, expires };
}

export const newRequestId = () => Math.random().toString(36).slice(2, 8) + Date.now().toString(36).slice(-4);

/** Start a workflow on main. Returns the request id that the run's title carries, to find the run. */
export async function dispatch(workflow: string, inputs: Record<string, string> = {}): Promise<string> {
  const request_id = newRequestId();
  await gh(`/repos/${REPO}/actions/workflows/${workflow}/dispatches`, {
    method: 'POST', body: JSON.stringify({ ref: DEFAULTS.branch, inputs: { ...inputs, request_id } }),
  });
  return request_id;
}

/** Find the run a dispatch started (its title ends with "[request_id]"). null while GitHub is still queuing it. */
export async function findRun(workflow: string, requestId: string): Promise<any | null> {
  const d: any = await gh(`/repos/${REPO}/actions/workflows/${workflow}/runs?event=workflow_dispatch&per_page=15`);
  return (d?.workflow_runs || []).find((r: any) => String(r.display_title || '').includes(`[${requestId}]`)) || null;
}

/** Live state of one run with its jobs and steps (not the 30-minute feed). */
export async function runLive(runId: number | string) {
  const [run, jobs]: any = await Promise.all([gh(`/repos/${REPO}/actions/runs/${runId}`), gh(`/repos/${REPO}/actions/runs/${runId}/jobs?per_page=100`)]);
  return { run, jobs: jobs?.jobs || [] };
}

export const comment = (issue: number, body: string) =>
  gh(`/repos/${REPO}/issues/${issue}/comments`, { method: 'POST', body: JSON.stringify({ body }) });

export const closeIssue = (issue: number) =>
  gh(`/repos/${REPO}/issues/${issue}`, { method: 'PATCH', body: JSON.stringify({ state: 'closed' }) });

export const cancelRun = (runId: number | string) => gh(`/repos/${REPO}/actions/runs/${runId}/cancel`, { method: 'POST' });

/** Board moves and topic edits go through the checked studio-action workflow. */
export const studioAction = (action: 'board-move' | 'topic-add' | 'topic-remove', args: Record<string, string>) =>
  dispatch('studio-action.yml', { action, args: JSON.stringify(args) });

export const githubUrl = (path = '') => `https://github.com/${REPO}${path}`;
