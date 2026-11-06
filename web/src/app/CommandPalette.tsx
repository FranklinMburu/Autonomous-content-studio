import React, { useState, useEffect, useRef } from 'react';
import {
  MagnifyingGlass,
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
  ArrowSquareOut,
  Sun,
  Moon,
} from '@phosphor-icons/react';
import { useStudio } from '../context/StudioContext';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectRoute?: (route: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose, onSelectRoute }) => {
  const { films, topics, studio, theme, setTheme, navigate } = useStudio();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const pages = [
    { name: 'Films', path: '/app/films', icon: FilmStrip, group: 'Go to' },
    { name: 'Runs', path: '/app/runs', icon: Path, group: 'Go to' },
    { name: 'Review', path: '/app/review', icon: Eye, group: 'Go to' },
    { name: 'Polish', path: '/app/polish', icon: MagicWand, group: 'Go to' },
    { name: 'Upload', path: '/app/upload', icon: UploadSimple, group: 'Go to' },
    { name: 'Channels', path: '/app/channels', icon: Broadcast, group: 'Go to' },
    { name: 'Topics', path: '/app/topics', icon: LightbulbFilament, group: 'Go to' },
    { name: 'Schedule', path: '/app/schedule', icon: CalendarDots, group: 'Go to' },
    { name: 'Memory', path: '/app/memory', icon: Archive, group: 'Go to' },
    { name: 'Brain', path: '/app/brain', icon: Brain, group: 'Go to' },
    { name: 'Lab', path: '/app/lab', icon: Flask, group: 'Go to' },
    { name: 'Guard', path: '/app/guard', icon: ShieldCheck, group: 'Go to' },
    { name: 'Analytics', path: '/app/analytics', icon: ChartLineUp, group: 'Go to' },
    { name: 'Trends', path: '/app/trends', icon: TrendUp, group: 'Go to' },
    { name: 'Publish', path: '/app/publish', icon: PaperPlaneTilt, group: 'Go to' },
    { name: 'Thumbnails', path: '/app/thumbnails', icon: ImageSquare, group: 'Go to' },
    { name: 'Voices', path: '/app/voices', icon: MicrophoneStage, group: 'Go to' },
    { name: 'Languages', path: '/app/languages', icon: Translate, group: 'Go to' },
    { name: 'Settings', path: '/app/settings', icon: GearSix, group: 'Go to' },
  ];

  const actions = [
    { name: 'New film', url: studio.links.newFilm(), icon: ArrowSquareOut, group: 'Actions', isExt: true },
    { name: 'Run next now', url: studio.links.runNow(), icon: ArrowSquareOut, group: 'Actions', isExt: true },
    { name: 'Edit topics', url: studio.links.topicsFile(), icon: ArrowSquareOut, group: 'Actions', isExt: true },
    {
      name: `Switch to ${theme === 'dark' ? 'Light' : 'Dark'} theme`,
      action: () => setTheme(theme === 'dark' ? 'light' : 'dark'),
      icon: theme === 'dark' ? Sun : Moon,
      group: 'Actions',
      isExt: false,
    },
  ];

  const filteredPages = pages.filter(p => p.name.toLowerCase().includes(query.toLowerCase()));
  const filteredFilms = films
    .filter(f => (f.title || '').toLowerCase().includes(query.toLowerCase()))
    .slice(0, 5)
    .map(f => ({
      name: f.title || f.id,
      path: `/app/films/${f.id}`,
      icon: FilmStrip,
      group: 'Films',
    }));

  const filteredTopics = topics
    .filter(t => t.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 5)
    .map(t => ({
      name: t,
      path: '/app/topics',
      icon: LightbulbFilament,
      group: 'Topics',
    }));

  const filteredActions = actions.filter(a => a.name.toLowerCase().includes(query.toLowerCase()));

  const allItems = [...filteredPages, ...filteredFilms, ...filteredTopics, ...filteredActions];

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  const handleSelect = (item: any) => {
    if (!item) return;
    if (item.action) {
      item.action();
    } else if (item.isExt && item.url) {
      window.open(item.url, '_blank', 'noopener,noreferrer');
    } else if (item.path) {
      if (onSelectRoute) {
        onSelectRoute(item.path);
      } else {
        navigate(item.path);
      }
    }
    onClose();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev + 1) % Math.max(1, allItems.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev - 1 + allItems.length) % Math.max(1, allItems.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (allItems[selectedIndex]) {
        handleSelect(allItems[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'rgba(5, 6, 10, 0.72)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '12vh',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '640px',
          maxWidth: '92vw',
          background: 'var(--s1)',
          borderRadius: '16px',
          boxShadow: '0 0 0 1px var(--line2), 0 30px 100px -20px rgba(0,0,0,0.85)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '75vh',
        }}
        onClick={e => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '16px 20px',
            borderBottom: '1px solid var(--line)',
          }}
        >
          <MagnifyingGlass size={20} color="var(--tx3)" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search or jump to..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--tx)',
              fontSize: '15px',
              fontFamily: 'inherit',
            }}
          />
          <span className="kbd">ESC</span>
        </div>

        <div style={{ overflowY: 'auto', padding: '10px 8px' }}>
          {allItems.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--tx3)', fontSize: '14px' }}>
              No matches found
            </div>
          ) : (
            allItems.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              const IconComp = item.icon;
              return (
                <div
                  key={`${item.group}-${item.name}-${idx}`}
                  onClick={() => handleSelect(item)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    height: '42px',
                    padding: '0 12px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(245,165,36,0.12)' : 'transparent',
                    boxShadow: isSelected ? '0 0 0 1px rgba(245,165,36,0.22) inset' : 'none',
                    color: isSelected ? 'var(--tx)' : 'var(--tx2)',
                    fontSize: '13.5px',
                  }}
                >
                  <IconComp
                    size={18}
                    weight="duotone"
                    color={isSelected ? 'var(--amber2)' : 'var(--tx3)'}
                    style={{ flexShrink: 0 }}
                  />
                  <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.name}
                  </span>
                  <span
                    style={{
                      fontSize: '11px',
                      color: 'var(--tx3)',
                      background: 'rgba(255,255,255,0.04)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {item.group}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
