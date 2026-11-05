import React, { useState } from 'react';
import {
  FilmStrip,
  Path,
  Eye,
  MagicWand,
  UploadSimple,
  Broadcast,
  LightbulbFilament,
  CalendarDots,
  Archive,
  Brain,
  Flask,
  ShieldCheck,
  ChartLineUp,
  TrendUp,
  PaperPlaneTilt,
  ImageSquare,
  MicrophoneStage,
  Translate,
  GearSix,
  CaretUpDown,
  CaretDown,
  CaretRight,
  MagnifyingGlass,
} from '@phosphor-icons/react';
import { Mark } from '../ui/Mark';
import { useStudio } from '../context/StudioContext';

interface SidebarProps {
  currentRoute: string;
  onNavigate: (route: string) => void;
  onOpenCommandPalette: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentRoute, onNavigate, onOpenCommandPalette }) => {
  const {
    runs,
    reviewItems,
    polishItems,
    uploadItems,
    topics,
    alerts,
    nextSlots,
  } = useStudio();

  const growPages = [
    '/app/analytics',
    '/app/trends',
    '/app/publish',
    '/app/thumbnails',
    '/app/voices',
    '/app/languages',
  ];

  const isGrowActive = growPages.some(p => currentRoute.startsWith(p));
  const [growExpanded, setGrowExpanded] = useState<boolean>(isGrowActive);
  const [channelMenuOpen, setChannelMenuOpen] = useState(false);

  // Compute live badges
  const runningCount = runs.filter(
    r => r.state === 'running' || r.state === 'queued' || r.state === 'in_progress'
  ).length;
  const reviewCount = reviewItems.length;
  const polishCount = polishItems.length;
  const uploadCount = uploadItems.length;
  const topicsCount = topics.length;
  const hasAlerts = alerts.length > 0;

  // Next film calculation
  const rawNext: any = nextSlots[0];
  const nextTime =
    rawNext instanceof Date
      ? rawNext.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
      : (rawNext ? String(rawNext) : '13:23');
  // Runs started today:
  const todayStr = new Date().toISOString().slice(0, 10);
  const startedToday = runs.filter(r => r.started && r.started.startsWith(todayStr)).length;
  const startedFraction = Math.min(1, Math.max(0.2, startedToday / 5));

  const isActive = (path: string) => {
    if (path === '/app/films') {
      return currentRoute === '/app' || currentRoute === '/app/films' || currentRoute.startsWith('/app/films/');
    }
    return currentRoute.startsWith(path);
  };

  return (
    <aside className="side">
      {/* Brand & Channel switcher */}
      <div className="brandrow">
        <Mark size={26} />
        <b>Candela</b>
        <span className="ws">Studio</span>
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setChannelMenuOpen(!channelMenuOpen)}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              color: 'inherit',
              padding: 0,
            }}
            title="Switch channel"
          >
            <CaretUpDown size={14} className="ic faint" />
          </button>
          {channelMenuOpen && (
            <div
              style={{
                position: 'absolute',
                top: '26px',
                right: '0',
                background: 'var(--s1)',
                boxShadow: '0 0 0 1px var(--line2), 0 12px 30px rgba(0,0,0,0.6)',
                borderRadius: '8px',
                padding: '6px',
                zIndex: 100,
                width: '180px',
              }}
            >
              <div
                onClick={() => {
                  onNavigate('/app/channels');
                  setChannelMenuOpen(false);
                }}
                style={{
                  padding: '8px 10px',
                  borderRadius: '6px',
                  fontSize: '12.5px',
                  color: 'var(--tx)',
                  cursor: 'pointer',
                  background: 'rgba(245,165,36,0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Broadcast size={14} color="var(--amber2)" />
                <span>Hidden Reasons</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Search / Command palette trigger */}
      <div className="search" onClick={onOpenCommandPalette} style={{ cursor: 'pointer' }}>
        <MagnifyingGlass size={15} className="ic" />
        <span>Search or jump to…</span>
        <span className="kbd">⌘K</span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', margin: '0 -6px', padding: '0 6px' }}>
        {/* WORKSPACE GROUP */}
        <div className="group">Workspace</div>

        <div
          className={`ni ${isActive('/app/films') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/films')}
          style={{ cursor: 'pointer' }}
        >
          <FilmStrip size={19} weight="duotone" className="ic" />
          <span>Films</span>
        </div>

        <div
          className={`ni ${isActive('/app/runs') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/runs')}
          style={{ cursor: 'pointer' }}
        >
          <Path size={19} weight="duotone" className="ic" />
          <span>Runs</span>
          {runningCount > 0 && <span className="nb">{runningCount}</span>}
        </div>

        <div
          className={`ni ${isActive('/app/review') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/review')}
          style={{ cursor: 'pointer' }}
        >
          <Eye size={19} weight="duotone" className="ic" />
          <span>Review</span>
          {reviewCount > 0 && <span className="nb">{reviewCount}</span>}
        </div>

        <div
          className={`ni ${isActive('/app/polish') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/polish')}
          style={{ cursor: 'pointer' }}
        >
          <MagicWand size={19} weight="duotone" className="ic" />
          <span>Polish</span>
          {polishCount > 0 && <span className="nb">{polishCount}</span>}
        </div>

        <div
          className={`ni ${isActive('/app/upload') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/upload')}
          style={{ cursor: 'pointer' }}
        >
          <UploadSimple size={19} weight="duotone" className="ic" />
          <span>Upload</span>
          {uploadCount > 0 && <span className="nb">{uploadCount}</span>}
        </div>

        {/* STUDIO GROUP */}
        <div className="group">Studio</div>

        <div
          className={`ni ${isActive('/app/channels') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/channels')}
          style={{ cursor: 'pointer' }}
        >
          <Broadcast size={19} weight="duotone" className="ic" />
          <span>Channels</span>
        </div>

        <div
          className={`ni ${isActive('/app/topics') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/topics')}
          style={{ cursor: 'pointer' }}
        >
          <LightbulbFilament size={19} weight="duotone" className="ic" />
          <span>Topics</span>
          {topicsCount > 0 && <span className="nb">{topicsCount}</span>}
        </div>

        <div
          className={`ni ${isActive('/app/schedule') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/schedule')}
          style={{ cursor: 'pointer' }}
        >
          <CalendarDots size={19} weight="duotone" className="ic" />
          <span>Schedule</span>
        </div>

        <div
          className={`ni ${isActive('/app/memory') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/memory')}
          style={{ cursor: 'pointer' }}
        >
          <Archive size={19} weight="duotone" className="ic" />
          <span>Memory</span>
        </div>

        {/* ENGINE GROUP */}
        <div className="group">Engine</div>

        <div
          className={`ni ${isActive('/app/brain') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/brain')}
          style={{ cursor: 'pointer' }}
        >
          <Brain size={19} weight="duotone" className="ic" />
          <span>Brain</span>
        </div>

        <div
          className={`ni ${isActive('/app/lab') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/lab')}
          style={{ cursor: 'pointer' }}
        >
          <Flask size={19} weight="duotone" className="ic" />
          <span>Lab</span>
        </div>

        <div
          className={`ni ${isActive('/app/guard') ? 'on' : ''}`}
          onClick={() => onNavigate('/app/guard')}
          style={{ cursor: 'pointer' }}
        >
          <ShieldCheck size={19} weight="duotone" className="ic" />
          <span>Guard</span>
          {hasAlerts && (
            <span
              style={{
                marginLeft: 'auto',
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                background: '#F85149',
              }}
            />
          )}
        </div>

        {/* GROW GROUP (COLLAPSED / EXPANDED) */}
        <div
          className="group grow"
          onClick={() => setGrowExpanded(!growExpanded)}
          style={{ cursor: 'pointer', userSelect: 'none' }}
        >
          <span>Grow</span>
          {!growExpanded && <span className="soon">6 soon</span>}
          {growExpanded ? (
            <CaretDown size={11} className="ic faint" />
          ) : (
            <CaretRight size={11} className="ic faint" />
          )}
        </div>

        {growExpanded && (
          <div>
            <div
              className={`ni ${isActive('/app/analytics') ? 'on' : ''}`}
              onClick={() => onNavigate('/app/analytics')}
              style={{ cursor: 'pointer' }}
            >
              <ChartLineUp size={19} weight="duotone" className="ic" />
              <span>Analytics</span>
              <span className="nb soonb">Soon</span>
            </div>

            <div
              className={`ni ${isActive('/app/trends') ? 'on' : ''}`}
              onClick={() => onNavigate('/app/trends')}
              style={{ cursor: 'pointer' }}
            >
              <TrendUp size={19} weight="duotone" className="ic" />
              <span>Trends</span>
              <span className="nb soonb">Soon</span>
            </div>

            <div
              className={`ni ${isActive('/app/publish') ? 'on' : ''}`}
              onClick={() => onNavigate('/app/publish')}
              style={{ cursor: 'pointer' }}
            >
              <PaperPlaneTilt size={19} weight="duotone" className="ic" />
              <span>Publish</span>
              <span className="nb soonb">Soon</span>
            </div>

            <div
              className={`ni ${isActive('/app/thumbnails') ? 'on' : ''}`}
              onClick={() => onNavigate('/app/thumbnails')}
              style={{ cursor: 'pointer' }}
            >
              <ImageSquare size={19} weight="duotone" className="ic" />
              <span>Thumbnails</span>
              <span className="nb soonb">Soon</span>
            </div>

            <div
              className={`ni ${isActive('/app/voices') ? 'on' : ''}`}
              onClick={() => onNavigate('/app/voices')}
              style={{ cursor: 'pointer' }}
            >
              <MicrophoneStage size={19} weight="duotone" className="ic" />
              <span>Voices</span>
              <span className="nb soonb">Soon</span>
            </div>

            <div
              className={`ni ${isActive('/app/languages') ? 'on' : ''}`}
              onClick={() => onNavigate('/app/languages')}
              style={{ cursor: 'pointer' }}
            >
              <Translate size={19} weight="duotone" className="ic" />
              <span>Languages</span>
              <span className="nb soonb">Soon</span>
            </div>
          </div>
        )}
      </div>

      {/* SIDEBAR FOOTER: NEXT FILM & OWNER */}
      <div className="side-foot">
        <div className="quota">
          <div className="qrow">
            <span>Next film</span>
            <b>{nextTime}</b>
          </div>
          <div className="bar">
            <i style={{ width: `${Math.round(startedFraction * 100)}%` }} />
          </div>
          <div className="qrow faint">
            <span>{startedToday} of 5 started today · $0</span>
          </div>
        </div>

        <div className="me">
          <div className="av">F</div>
          <div>
            <b>Franklin</b>
            <span>Owner</span>
          </div>
          <div
            onClick={() => onNavigate('/app/settings')}
            style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}
            title="Settings"
          >
            <GearSix size={17} className="ic" />
          </div>
        </div>
      </div>
    </aside>
  );
};
