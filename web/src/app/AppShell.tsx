import React, { useState, useEffect } from 'react';
import {
  FilmStrip,
  Path,
  Eye,
  Broadcast,
  DotsThreeOutline,
  WarningCircle,
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
import { ChannelsView } from './views/ChannelsView';
import { ChannelDetailView } from './views/ChannelDetailView';
import { TopicsView } from './views/TopicsView';
import { ScheduleView } from './views/ScheduleView';
import { MemoryView } from './views/MemoryView';
import { BrainView } from './views/BrainView';
import { LabView } from './views/LabView';
import { GuardView } from './views/GuardView';
import { SoonView } from './views/SoonView';
import { SettingsView } from './views/SettingsView';
import { NotFoundView } from './views/NotFoundView';
import { useStudio } from '../context/StudioContext';
import { Mark } from '../ui/Mark';

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
  const [internalRoute, setInternalRoute] = useState<string>(embeddedRoute || '/app/films');
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [moreSheetOpen, setMoreSheetOpen] = useState(false);

  // Sync internal route with prop if embedded
  useEffect(() => {
    if (embedded && embeddedRoute && embeddedRoute !== internalRoute) {
      setInternalRoute(embeddedRoute);
    }
  }, [embedded, embeddedRoute]);

  const activeRoute = embedded ? internalRoute : (currentPath.startsWith('/app') ? currentPath : '/app/films');

  const handleNavigate = (route: string) => {
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
    // Films detail
    if (activeRoute.startsWith('/app/films/')) {
      const filmId = activeRoute.replace('/app/films/', '');
      return <FilmDetailView filmId={filmId} onBack={() => handleNavigate('/app/films')} />;
    }
    // Channel detail
    if (activeRoute.startsWith('/app/channels/')) {
      const chCode = activeRoute.replace('/app/channels/', '');
      return (
        <ChannelDetailView
          channelCode={chCode}
          onBack={() => handleNavigate('/app/channels')}
          onSelectFilm={id => handleNavigate(`/app/films/${id}`)}
          onNavigate={handleNavigate}
        />
      );
    }

    switch (activeRoute) {
      case '/app':
      case '/app/films':
        return (
          <FilmsView
            onSelectFilm={id => handleNavigate(`/app/films/${id}`)}
            onNavigate={handleNavigate}
          />
        );
      case '/app/runs':
        return <RunsView />;
      case '/app/review':
        return <ReviewView />;
      case '/app/polish':
        return <PolishView />;
      case '/app/upload':
        return <UploadView />;
      case '/app/channels':
        return <ChannelsView onSelectChannel={code => handleNavigate(`/app/channels/${code}`)} />;
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
      case '/app/analytics':
        return <SoonView page="analytics" onBackToFilms={() => handleNavigate('/app/films')} />;
      case '/app/trends':
        return <SoonView page="trends" onBackToFilms={() => handleNavigate('/app/films')} />;
      case '/app/publish':
        return <SoonView page="publish" onBackToFilms={() => handleNavigate('/app/films')} />;
      case '/app/thumbnails':
        return <SoonView page="thumbnails" onBackToFilms={() => handleNavigate('/app/films')} />;
      case '/app/voices':
        return <SoonView page="voices" onBackToFilms={() => handleNavigate('/app/films')} />;
      case '/app/languages':
        return <SoonView page="languages" onBackToFilms={() => handleNavigate('/app/films')} />;
      case '/app/settings':
        return <SettingsView />;
      default:
        return <NotFoundView />;
    }
  };

  // Compute page display name for topbar breadcrumb
  const getPageName = () => {
    if (activeRoute.startsWith('/app/films/')) return 'Film Detail';
    if (activeRoute.startsWith('/app/channels/')) return 'Channel Detail';
    const sub = activeRoute.replace('/app/', '');
    if (!sub || sub === '/app') return 'Films';
    return sub.charAt(0).toUpperCase() + sub.slice(1);
  };

  return (
    <div
      className="app"
      style={{
        position: embedded ? 'absolute' : 'fixed',
        inset: 0,
        overflow: 'hidden',
        width: embedded ? '1440px' : '100%',
        height: embedded ? '887px' : '100%',
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
        <Topbar pageName={getPageName()} />
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', position: 'relative' }}>
          {renderView()}
        </div>
      </div>

      {/* Mobile Bottom Tab Bar (shown when screen is mobile width < 640px) */}
      <div
        className="mobile-tab-bar"
        style={{
          display: 'none', // Controlled via media query in candela.css / inline style
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          height: '56px',
          background: 'rgba(14,14,18,0.92)',
          backdropFilter: 'blur(16px)',
          borderTop: '1px solid var(--line)',
          zIndex: 50,
          justifyContent: 'space-around',
          alignItems: 'center',
          paddingBottom: 'env(safe-area-inset-bottom, 0px)',
        }}
      >
        <button
          onClick={() => handleNavigate('/app/films')}
          style={{ background: 'none', border: 'none', color: activeRoute.startsWith('/app/films') ? 'var(--amber2)' : 'var(--tx3)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', cursor: 'pointer' }}
        >
          <FilmStrip size={20} weight="duotone" />
          <span style={{ fontSize: '10px' }}>Films</span>
        </button>
        <button
          onClick={() => handleNavigate('/app/runs')}
          style={{ background: 'none', border: 'none', color: activeRoute.startsWith('/app/runs') ? 'var(--amber2)' : 'var(--tx3)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', cursor: 'pointer' }}
        >
          <Path size={20} weight="duotone" />
          <span style={{ fontSize: '10px' }}>Runs</span>
        </button>
        <button
          onClick={() => handleNavigate('/app/review')}
          style={{ background: 'none', border: 'none', color: activeRoute.startsWith('/app/review') ? 'var(--amber2)' : 'var(--tx3)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', cursor: 'pointer' }}
        >
          <Eye size={20} weight="duotone" />
          <span style={{ fontSize: '10px' }}>Review</span>
        </button>
        <button
          onClick={() => handleNavigate('/app/channels')}
          style={{ background: 'none', border: 'none', color: activeRoute.startsWith('/app/channels') ? 'var(--amber2)' : 'var(--tx3)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', cursor: 'pointer' }}
        >
          <Broadcast size={20} weight="duotone" />
          <span style={{ fontSize: '10px' }}>Channels</span>
        </button>
        <button
          onClick={() => setMoreSheetOpen(!moreSheetOpen)}
          style={{ background: 'none', border: 'none', color: 'var(--tx3)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', cursor: 'pointer' }}
        >
          <DotsThreeOutline size={20} weight="duotone" />
          <span style={{ fontSize: '10px' }}>More</span>
        </button>
      </div>

      {/* Command Palette */}
      <CommandPalette
        isOpen={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        onSelectRoute={handleNavigate}
      />
    </div>
  );
};
