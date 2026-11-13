import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { ActionError, checkConnection, Connection, dispatch, findRun, forgetToken, getToken, runLive, setToken } from '../lib/actions';
import { useStudio } from './StudioContext';

// Everything the owner starts from the app is a "task": we follow it from "sent" to the GitHub run it started, live,
// until it is done, then refresh the data. Tasks survive a reload (this browser only).

export interface Task {
  id: string;
  label: string;            // what the owner did, in plain words ("Make Shorts from N3on's stream")
  workflow?: string;        // the workflow file it started (none for a direct action like a comment)
  requestId?: string;
  runId?: number;
  runUrl?: string;
  state: 'sending' | 'queued' | 'running' | 'success' | 'failure' | 'cancelled' | 'done' | 'error';
  step?: string;            // the job/step running now
  progress?: [number, number];
  started: number;
  finished?: number;
  error?: string;
  next?: string;            // what happens after it is done
  target?: string;          // a route to open (the video, the run)
}

interface ActionsValue {
  connection: Connection | null;
  connecting: boolean;
  connectError: string;
  connect: (token: string) => Promise<boolean>;
  disconnect: () => void;
  hasToken: boolean;
  tasks: Task[];
  start: (label: string, workflow: string, inputs?: Record<string, string>, opts?: { next?: string; target?: string }) => Promise<Task | null>;
  act: (label: string, fn: () => Promise<any>, opts?: { next?: string; target?: string }) => Promise<boolean>;
  dismiss: (id: string) => void;
  needToken: boolean;
  setNeedToken: (v: boolean) => void;
}

const Ctx = createContext<ActionsValue | null>(null);
const STORE = 'candela:tasks';

export const ActionsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { refresh } = useStudio();
  const [connection, setConnection] = useState<Connection | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [connectError, setConnectError] = useState('');
  const [hasToken, setHasToken] = useState(() => !!getToken());
  const [needToken, setNeedToken] = useState(false);
  const [tasks, setTasks] = useState<Task[]>(() => {
    try { return (JSON.parse(localStorage.getItem(STORE) || '[]') as Task[]).filter(t => Date.now() - t.started < 864e5); } catch { return []; }
  });
  const tasksRef = useRef(tasks);
  tasksRef.current = tasks;

  useEffect(() => { try { localStorage.setItem(STORE, JSON.stringify(tasks.slice(0, 30))); } catch { /* ignore */ } }, [tasks]);

  useEffect(() => {
    if (!getToken()) return;
    checkConnection().then(setConnection).catch(() => setConnection(null));
  }, []);

  const connect = useCallback(async (token: string) => {
    setConnecting(true); setConnectError('');
    setToken(token);
    try {
      const c = await checkConnection();
      if (!c.canAct) {
        setConnectError('GitHub accepted the token, but it cannot start workflows here. Make sure it is for the repository Autonomous-content-studio with "Actions" and "Issues" set to "Read and write".');
        setConnection(c); setHasToken(true); return false;
      }
      setConnection(c); setHasToken(true); setNeedToken(false); return true;
    } catch (e: any) {
      forgetToken(); setHasToken(false); setConnection(null);
      setConnectError(e?.message || 'Could not connect.'); return false;
    } finally { setConnecting(false); }
  }, []);

  const disconnect = useCallback(() => { forgetToken(); setConnection(null); setHasToken(false); }, []);

  const patch = (id: string, p: Partial<Task>) => setTasks(ts => ts.map(t => (t.id === id ? { ...t, ...p } : t)));

  const start = useCallback(async (label: string, workflow: string, inputs: Record<string, string> = {}, opts: { next?: string; target?: string } = {}) => {
    if (!getToken()) { setNeedToken(true); return null; }
    const id = Math.random().toString(36).slice(2);
    const t: Task = { id, label, workflow, state: 'sending', started: Date.now(), ...opts };
    setTasks(ts => [t, ...ts]);
    try {
      const requestId = await dispatch(workflow, inputs);
      patch(id, { requestId, state: 'queued', step: 'GitHub is starting it (usually under a minute)' });
      return { ...t, requestId, state: 'queued' as const };
    } catch (e: any) {
      if (e instanceof ActionError && (e.kind === 'no-token' || e.kind === 'bad-token')) setNeedToken(true);
      patch(id, { state: 'error', error: e?.message || 'Could not start it.', finished: Date.now() });
      return null;
    }
  }, []);

  const act = useCallback(async (label: string, fn: () => Promise<any>, opts: { next?: string; target?: string } = {}) => {
    if (!getToken()) { setNeedToken(true); return false; }
    const id = Math.random().toString(36).slice(2);
    setTasks(ts => [{ id, label, state: 'sending', started: Date.now(), ...opts }, ...ts]);
    try {
      await fn();
      patch(id, { state: 'done', finished: Date.now() });
      setTimeout(() => refresh(), 4000);
      return true;
    } catch (e: any) {
      if (e instanceof ActionError && (e.kind === 'no-token' || e.kind === 'bad-token')) setNeedToken(true);
      patch(id, { state: 'error', error: e?.message || 'It did not work.', finished: Date.now() });
      return false;
    }
  }, [refresh]);

  // follow every open task: find its run, then its steps, every 8 s (only while the page is visible)
  useEffect(() => {
    const tick = async () => {
      if (document.visibilityState !== 'visible' || !getToken()) return;
      for (const t of tasksRef.current.filter(t => t.workflow && ['queued', 'running'].includes(t.state))) {
        try {
          if (!t.runId) {
            const r = await findRun(t.workflow!, t.requestId!);
            if (r) patch(t.id, { runId: r.id, runUrl: r.html_url, state: r.status === 'completed' ? (r.conclusion || 'failure') : 'running' });
            else if (Date.now() - t.started > 5 * 60e3) patch(t.id, { step: 'Still waiting for GitHub to start it (GitHub can be slow; it will start)' });
            continue;
          }
          const { run, jobs } = await runLive(t.runId);
          const steps = jobs.flatMap((j: any) => j.steps.map((s: any) => ({ job: j.name, ...s })));
          const live = steps.find((s: any) => s.status === 'in_progress');
          const done = steps.filter((s: any) => s.status === 'completed').length;
          if (run.status === 'completed') {
            patch(t.id, { state: run.conclusion === 'success' ? 'success' : run.conclusion === 'cancelled' ? 'cancelled' : 'failure', finished: Date.now(), step: undefined, progress: [done, steps.length] });
            refresh();
          } else {
            patch(t.id, { state: 'running', step: live ? `${live.job}: ${live.name}` : 'Starting', progress: [done, steps.length] });
          }
        } catch { /* try again next tick */ }
      }
    };
    const timer = setInterval(tick, 8000);
    tick();
    return () => clearInterval(timer);
  }, [refresh]);

  const dismiss = useCallback((id: string) => setTasks(ts => ts.filter(t => t.id !== id)), []);

  const value = useMemo(() => ({ connection, connecting, connectError, connect, disconnect, hasToken, tasks, start, act, dismiss, needToken, setNeedToken }),
    [connection, connecting, connectError, connect, disconnect, hasToken, tasks, start, act, dismiss, needToken]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
};

export const useActions = () => {
  const c = useContext(Ctx);
  if (!c) throw new Error('useActions must be inside ActionsProvider');
  return c;
};
