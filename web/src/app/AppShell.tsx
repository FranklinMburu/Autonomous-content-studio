import React, { useState, useEffect } from 'react';
import {
  House,
  Kanban,
  Plus,
  Books,
  DotsThreeOutline,
  WarningCircle,
  X,
} from '@phosphor-icons/react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { CommandPalette } from './CommandPalette';
import { FilmsView } from './views/FilmsView';
import { FilmDetailView } from './views/FilmDetailView';
import { RunsView } from './views/RunsView';
import { ReviewView } from './views/ReviewView';
import { PolishView } from './views/PolishView';
import { UploadView } from './views/UploadView';
import { TopicsView } from './views/TopicsView';
import { ScheduleView } from './views/ScheduleView';
import { MemoryView } from './views/MemoryView';
import { BrainView } from './views/BrainView';
import { LabView } from './views/LabView';
import { GuardView } from './views/GuardView';
import { SettingsView } from './views/SettingsView';
import { NotFoundView } from './views/NotFoundView';
import { useStudio } from '../context/StudioContext';
import { HomeView } from './views/HomeView';
import { BoardView } from './views/BoardView';
import { LibraryView } from './views/LibraryView';
import { MakeView } from './views/MakeView';
import { GuideView } from './views/GuideView';
import { ChannelView } from './views/ChannelView';
import { VideoView } from './views/VideoView';
import { ActivityTray, ConnectSheet } from './kit';
import { CHANNELS, channelOf } from '../lib/channels';

export interface AppShellProps {
  embedded?: boolean;
  embeddedRoute?: string;
  onEmbeddedRouteChange?: (r: string) => void;
  onFirstInteraction?: () => void;
}

export const AppShell: React.FC<AppShellProps> = ({
  embedded = false,
  embeddedRoute,
  onEmbeddedRouteChange,
  onFirstInteraction,
}) => {
  const { currentPath, navigate, error, refresh } = useStudio();
  const [internalRoute, setInternalRoute] = useState<string>(embeddedRoute || '/app');
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [moreSheetOpen, setMoreSheetOpen] = useState(false);

  // Sync internal route with prop if embedded
  useEffect(() => {
    if (embedded && embeddedRoute && embeddedRoute !== internalRoute) {
      setInternalRoute(embeddedRoute);
    }
  }, [embedded, embeddedRoute]);

  const fullRoute = embedded ? internalRoute : (currentPath.startsWith('/app') ? currentPath : '/app');
  const activeRoute = fullRoute.split('?')[0].replace(/\/$/, '') || '/app';

  const handleNavigate = (route: string) => {
    setMoreSheetOpen(false);
    if (onFirstInteraction) onFirstInteraction();
    if (embedded) {
      setInternalRoute(route);
      if (onEmbeddedRouteChange) onEmbeddedRouteChange(route);
    } else {
      navigate(route);
    }
  };

  // Keyboard shortcut for command palette
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  // Determine which page view to render
  const renderView = () => {
    // a video of any channel (Shorts, motion videos)
    if (activeRoute.startsWith('/app/v/')) {
      return <VideoView key={activeRoute} id={decodeURIComponent(activeRoute.replace('/app/v/', ''))} onNavigate={handleNavigate} />;
    }
    // a channel
    if (activeRoute.startsWith('/app/c/')) {
      const code = activeRoute.replace('/app/c/', '').toUpperCase();
      return <ChannelView key={code + fullRoute} code={code} onNavigate={handleNavigate} />;
    }
    // Films detail
    if (activeRoute.startsWith('/app/films/')) {
      const filmId = activeRoute.replace('/app/films/', '');
      return <FilmDetailView filmId={filmId} onBack={() => handleNavigate('/app/films')} />;
    }
    // Channel detail
    if (activeRoute.startsWith('/app/channels/')) {
      const code = activeRoute.replace('/app/channels/', '').toUpperCase();
      return <ChannelView key={code} code={channelOf(code) ? code : 'HR'} onNavigate={handleNavigate} />;
    }
    // Runs detail
    if (activeRoute.startsWith('/app/runs/')) {
      const runId = activeRoute.replace('/app/runs/', '');
      return (
        <RunsView
          initialRunId={runId}
          onBack={() => handleNavigate('/app/runs')}
          onSelectRun={id => handleNavigate(`/app/runs/${id}`)}
        />
      );
    }
    // Review detail
    if (activeRoute.startsWith('/app/review/')) {
      const issueNumber = activeRoute.replace('/app/review/', '');
      return (
        <ReviewView
          initialIssueId={issueNumber}
          onBack={() => handleNavigate('/app/review')}
          onSelectIssue={num => handleNavigate(`/app/review/${num}`)}
        />
      );
    }

    switch (activeRoute) {
      case '/app':
        return <HomeView onNavigate={handleNavigate} />;
      case '/app/board':
        return <BoardView key={fullRoute} onNavigate={handleNavigate} />;
      case '/app/library':
        return <LibraryView key={fullRoute} onNavigate={handleNavigate} />;
      case '/app/make':
        return <MakeView key={fullRoute} onNavigate={handleNavigate} />;
      case '/app/guide':
        return <GuideView onNavigate={handleNavigate} />;
      case '/app/films':
        return (
          <FilmsView
            onSelectFilm={id => handleNavigate(`/app/films/${id}`)}
            onNavigate={handleNavigate}
          />
        );
      case '/app/runs':
        return <RunsView onSelectRun={id => handleNavigate(`/app/runs/${id}`)} />;
      case '/app/review':
        return <ReviewView onSelectIssue={num => handleNavigate(`/app/review/${num}`)} />;
      case '/app/polish':
        return <PolishView />;
      case '/app/upload':
        return <UploadView />;
      case '/app/channels':
        return <HomeView onNavigate={handleNavigate} />;
      case '/app/topics':
        return <TopicsView />;
      case '/app/schedule':
        return <ScheduleView />;
      case '/app/memory':
        return <MemoryView />;
      case '/app/brain':
        return <BrainView />;
      case '/app/lab':
        return <LabView />;
      case '/app/guard':
        return <GuardView />;
      case '/app/settings':
        return <SettingsView />;
      default:
        return <NotFoundView />;
    }
  };

  // Compute page display name for topbar breadcrumb
  const getPageName = (): [string, string | undefined] => {
    const r = activeRoute;
    if (r.startsWith('/app/v/')) return ['Video', undefined];
    if (r.startsWith('/app/c/')) { const c = channelOf(r.replace('/app/c/', '').toUpperCase()); return [c ? c.name : 'Channel', 'Channels']; }
    if (r.startsWith('/app/films/')) return ['Film', 'Hidden Reasons'];
    if (r.startsWith('/app/runs/')) return ['Run', 'Runs'];
    if (r.startsWith('/app/review/')) return ['Review', 'Hidden Reasons'];
    const names: Record<string, [string, string | undefined]> = {
      '/app': ['Home', undefined], '/app/board': ['Board', undefined], '/app/library': ['Library', undefined], '/app/make': ['Make', undefined],
      '/app/guide': ['How it works', undefined], '/app/runs': ['Runs', 'System'], '/app/brain': ['Brain', 'System'], '/app/lab': ['Lab', 'System'],
      '/app/guard': ['Guard', 'System'], '/app/settings': ['Settings', undefined], '/app/films': ['Films', 'Hidden Reasons'],
      '/app/review': ['Review', 'Hidden Reasons'], '/app/polish': ['Polish', 'Hidden Reasons'], '/app/upload': ['Upload', 'Hidden Reasons'],
      '/app/topics': ['Topics', 'Hidden Reasons'], '/app/schedule': ['Schedule', 'Hidden Reasons'], '/app/memory': ['Memory', 'Hidden Reasons'],
    };
    return names[r] || ['Studio', undefined];
  };
  const [pageName, section] = getPageName();

  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;

  return (
    <div
      className="app"
      style={{
        position: embedded ? 'absolute' : 'fixed',
        inset: 0,
        overflow: 'hidden',
        width: embedded && !isMobile ? '1440px' : '100%',
        height: embedded && !isMobile ? '887px' : '100%',
      }}
      onClick={onFirstInteraction}
    >
      {/* Rate Limit / Network Error Banner */}
      {error && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '32px',
            background: 'linear-gradient(90deg, #261614, #1E1210)',
            borderBottom: '1px solid rgba(248,81,73,0.3)',
            color: '#FF7B72',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            zIndex: 1000,
          }}
        >
          <WarningCircle size={14} />
          <span>{error.message}</span>
          <button
            onClick={() => refresh()}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--amber2)',
              cursor: 'pointer',
              fontSize: '12px',
              textDecoration: 'underline',
              padding: 0,
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Desktop Sidebar (visible on desktop >= 640px) */}
      <Sidebar
        currentRoute={activeRoute}
        onNavigate={handleNavigate}
        onOpenCommandPalette={() => setPaletteOpen(true)}
      />

      {/* Main Layout Area */}
      <div className="main" style={{ marginTop: error ? '32px' : 0 }}>
        <Topbar pageName={pageName} section={section} onNavigate={handleNavigate} />
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', position: 'relative' }}>
          {renderView()}
        </div>
      </div>

      {/* Phone tab bar: the 4 places people use most + More (everything else) */}
      <nav className="mobile-tab-bar" aria-label="Main" style={{ position: embedded ? 'absolute' : 'fixed' }}>
        <button className={`mtab${activeRoute === '/app' ? ' on' : ''}`} onClick={() => handleNavigate('/app')}><House size={20} weight="duotone" /><span>Home</span></button>
        <button className={`mtab${activeRoute === '/app/board' ? ' on' : ''}`} onClick={() => handleNavigate('/app/board')}><Kanban size={20} weight="duotone" /><span>Board</span></button>
        <button className={`mtab${activeRoute === '/app/make' ? ' on' : ''}`} onClick={() => handleNavigate('/app/make')}><Plus size={20} weight="duotone" /><span>Make</span></button>
        <button className={`mtab${activeRoute === '/app/library' || activeRoute.startsWith('/app/v/') ? ' on' : ''}`} onClick={() => handleNavigate('/app/library')}><Books size={20} weight="duotone" /><span>Library</span></button>
        <button className={`mtab${moreSheetOpen ? ' on' : ''}`} onClick={() => setMoreSheetOpen(!moreSheetOpen)} aria-expanded={moreSheetOpen}><DotsThreeOutline size={20} weight="duotone" /><span>More</span></button>
      </nav>
      {moreSheetOpen && (
        <div className="msheet-bg" onClick={() => setMoreSheetOpen(false)}>
          <div className="msheet more" role="dialog" aria-label="Everything" onClick={e => e.stopPropagation()}>
            <div className="msheet-h"><b>Everything</b><button aria-label="Close" onClick={() => setMoreSheetOpen(false)}><X size={16} /></button></div>
            <div className="more-g"><span>Channels</span>
              {CHANNELS.map(c => <button key={c.code} onClick={() => handleNavigate(`/app/c/${c.code}`)}><i style={{ background: c.color }}>{c.code}</i>{c.name}</button>)}
            </div>
            <div className="more-g"><span>Hidden Reasons desk</span>
              {[['Review', '/app/review'], ['Polish', '/app/polish'], ['Upload', '/app/upload'], ['Topics', '/app/topics'], ['Schedule', '/app/schedule'], ['Memory', '/app/memory']].map(([l, r]) =>
                <button key={r} onClick={() => handleNavigate(r)}>{l}</button>)}
            </div>
            <div className="more-g"><span>System</span>
              {[['Runs', '/app/runs'], ['Brain', '/app/brain'], ['Lab', '/app/lab'], ['Guard', '/app/guard'], ['How it works', '/app/guide'], ['Settings', '/app/settings']].map(([l, r]) =>
                <button key={r} onClick={() => handleNavigate(r)}>{l}</button>)}
            </div>
          </div>
        </div>
      )}

      {!embedded && <ActivityTray onOpen={handleNavigate} />}
      {!embedded && <ConnectSheet />}

      {/* Command Palette */}
      <CommandPalette
        isOpen={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onSelectRoute={handleNavigate}
      />
    </div>
  );
};
