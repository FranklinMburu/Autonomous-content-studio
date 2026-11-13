import React from 'react';
import { House, Kanban, Books, Plus, Path, Brain, Flask, ShieldCheck, BookOpenText, GearSix, MagnifyingGlass } from '@phosphor-icons/react';
import { Mark } from '../ui/Mark';
import { useStudio } from '../context/StudioContext';
import { useActions } from '../context/ActionsContext';
import { useItems } from '../lib/items';
import { CHANNELS } from '../lib/channels';

interface SidebarProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
  onOpenCommandPalette: () => void;
}

// The map of the app (13 Nov 2026 redesign): the work first (Home, Board, Library, Make), then one entry per channel,
// then the system. Same order as the Notion workspace: project -> channels -> board.
export const Sidebar: React.FC<SidebarProps> = ({ currentRoute, onNavigate, onOpenCommandPalette }) => {
  const { runs, alerts, nextSlots, scheduleData } = useStudio();
  const { connection, hasToken } = useActions();
  const items = useItems();
  const route = currentRoute.split('?')[0];
  const needs = items.filter(i => i.needsYou);
  const running = runs.filter((r: any) => r.state === 'running' || r.state === 'queued').length;

  const is = (p: string) => (p === '/app' ? route === '/app' || route === '/app/' : route === p || route.startsWith(p + '/'));
  const chOn = (code: string) => route === `/app/c/${code}` || (code === 'HR' && /^\/app\/(films|review|polish|upload|topics|schedule|memory)/.test(route));

  const Item: React.FC<{ to: string; icon: React.ReactNode; label: string; badge?: number | string; dot?: boolean; on?: boolean; hot?: boolean }> =
    ({ to, icon, label, badge, dot, on, hot }) => (
      <button className={`ni${(on ?? is(to)) ? ' on' : ''}`} onClick={() => onNavigate(to)} aria-current={(on ?? is(to)) ? 'page' : undefined}>
        {icon}<span>{label}</span>
        {badge ? <span className={`nb${hot ? ' hot' : ''}`}>{badge}</span> : null}
        {dot && <span className="ndot" />}
      </button>
    );

  const next = nextSlots[0];
  return (
    <aside className="side" aria-label="Main">
      <div className="brandrow">
        <Mark size={26} />
        <b>Candela</b>
        <span className="ws">Studio</span>
      </div>
      <button className="search" onClick={onOpenCommandPalette}>
        <MagnifyingGlass size={15} className="ic" />
        <span>Search or jump to…</span>
        <span className="kbd">⌘K</span>
      </button>

      <nav className="side-nav">
        <Item to="/app" icon={<House size={19} weight="duotone" className="ic" />} label="Home" badge={needs.length || undefined} hot />
        <Item to="/app/board" icon={<Kanban size={19} weight="duotone" className="ic" />} label="Board" />
        <Item to="/app/library" icon={<Books size={19} weight="duotone" className="ic" />} label="Library" />
        <Item to="/app/make" icon={<Plus size={19} weight="bold" className="ic" />} label="Make" />

        <div className="group">Channels</div>
        {CHANNELS.map(c => {
          const n = items.filter(i => i.lane === c.code && i.needsYou).length;
          return (
            <Item key={c.code} to={`/app/c/${c.code}`} on={chOn(c.code)} label={c.name} badge={n || undefined} hot
                  icon={<span className="chdot" style={{ background: c.color }} aria-hidden>{c.code}</span>} />
          );
        })}

        <div className="group">System</div>
        <Item to="/app/runs" icon={<Path size={19} weight="duotone" className="ic" />} label="Runs" badge={running || undefined} />
        <Item to="/app/brain" icon={<Brain size={19} weight="duotone" className="ic" />} label="Brain" />
        <Item to="/app/lab" icon={<Flask size={19} weight="duotone" className="ic" />} label="Lab" />
        <Item to="/app/guard" icon={<ShieldCheck size={19} weight="duotone" className="ic" />} label="Guard" dot={alerts.length > 0} />
        <Item to="/app/guide" icon={<BookOpenText size={19} weight="duotone" className="ic" />} label="How it works" />
      </nav>

      <div className="side-foot">
        {next && (
          <button className="quota" onClick={() => onNavigate('/app/schedule')}>
            <div className="qrow"><span>Next Hidden Reasons film</span><b>{next.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}</b></div>
            <div className="qrow faint"><span>{scheduleData?.utc?.length || 5} a day at most · $0</span></div>
          </button>
        )}
        <div className="me">
          <div className="av">F</div>
          <div>
            <b>Franklin</b>
            <span>{hasToken && connection?.canAct ? 'Owner · can act' : 'Watching · connect to act'}</span>
          </div>
          <button onClick={() => onNavigate('/app/settings')} title="Settings" aria-label="Settings" className="ib"><GearSix size={17} className="ic" /></button>
        </div>
      </div>
    </aside>
  );
};
