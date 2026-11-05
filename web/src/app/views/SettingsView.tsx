import React from 'react';
import { GearSix, Sun, Moon, Desktop, ArrowSquareOut, Trash } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';
import { DEFAULTS } from '../../lib/github-data.js';

export const SettingsView: React.FC = () => {
  const { theme, setTheme, clearCache } = useStudio();

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Settings</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Theme preferences, data sources and local caching.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: '640px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Theme Settings */}
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
          }}
        >
          <b style={{ fontSize: '15px', display: 'block', marginBottom: '6px' }}>Appearance</b>
          <p style={{ fontSize: '13px', color: 'var(--tx2)', marginBottom: '16px' }}>
            Choose between dark ink and light studio theme.
          </p>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => setTheme('dark')}
              className={`btn ${theme === 'dark' ? 'pri' : 'sec'}`}
              style={{ flex: 1, justifyContent: 'center', height: '38px', fontSize: '13px', cursor: 'pointer' }}
            >
              <Moon size={16} />
              <span>Dark ink</span>
            </button>
            <button
              onClick={() => setTheme('light')}
              className={`btn ${theme === 'light' ? 'pri' : 'sec'}`}
              style={{ flex: 1, justifyContent: 'center', height: '38px', fontSize: '13px', cursor: 'pointer' }}
            >
              <Sun size={16} />
              <span>Light</span>
            </button>
            <button
              onClick={() => setTheme('system')}
              className={`btn ${theme === 'system' ? 'pri' : 'sec'}`}
              style={{ flex: 1, justifyContent: 'center', height: '38px', fontSize: '13px', cursor: 'pointer' }}
            >
              <Desktop size={16} />
              <span>System</span>
            </button>
          </div>
        </div>

        {/* Data Source */}
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
          }}
        >
          <b style={{ fontSize: '15px', display: 'block', marginBottom: '6px' }}>Data source</b>
          <p style={{ fontSize: '13px', color: 'var(--tx2)', marginBottom: '14px' }}>
            Read directly from GitHub REST API & raw repositories with public unauthenticated caching.
          </p>
          <div
            style={{
              padding: '12px 14px',
              borderRadius: '10px',
              background: '#07080D',
              border: '1px solid var(--line)',
              fontFamily: 'ui-monospace, Menlo, monospace',
              fontSize: '12px',
              color: 'var(--tx2)',
              marginBottom: '10px',
            }}
          >
            <div>Repo: {DEFAULTS.owner}/{DEFAULTS.repo}</div>
            <div>Branch: {DEFAULTS.branch}</div>
            <div>Cache TTL: {DEFAULTS.cacheSeconds}s</div>
          </div>
          <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>
            To configure a different repository, modify DEFAULTS in github-data.js.
          </span>
        </div>

        {/* Cache clear */}
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <b style={{ fontSize: '15px', display: 'block' }}>Local Cache</b>
            <span style={{ fontSize: '13px', color: 'var(--tx2)' }}>
              Clear sessionStorage cache to force fresh fetch from GitHub.
            </span>
          </div>
          <button
            onClick={clearCache}
            className="btn sec"
            style={{ height: '36px', fontSize: '13px', cursor: 'pointer' }}
          >
            <Trash size={15} />
            <span>Clear cache</span>
          </button>
        </div>

        {/* About */}
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
            fontSize: '13px',
            color: 'var(--tx2)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <b style={{ fontSize: '15px', color: 'var(--tx)' }}>About Candela Studio</b>
          <span>Version 1.0.0 (v4 build specification approved Nov 2026)</span>
          <div style={{ display: 'flex', gap: '16px', marginTop: '6px' }}>
            <a
              href="https://github.com/FranklinMburu/Autonomous-content-studio"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--amber2)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <span>GitHub Repository</span>
              <ArrowSquareOut size={12} />
            </a>
            <a
              href="https://github.com/FranklinMburu/Autonomous-content-studio#readme"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--amber2)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <span>Documentation</span>
              <ArrowSquareOut size={12} />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
