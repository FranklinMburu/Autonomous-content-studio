import React, { useState } from 'react';
import { Broadcast, Bell, Plus, ArrowSquareOut } from '@phosphor-icons/react';
import { useStudio } from '../context/StudioContext';

interface TopbarProps {
  pageName: string;
}

export const Topbar: React.FC<TopbarProps> = ({ pageName }) => {
  const { studio, alerts } = useStudio();
  const [alertsOpen, setAlertsOpen] = useState(false);

  const hasAlerts = alerts && alerts.length > 0;

  return (
    <header className="top">
      <div className="crumb">
        <Broadcast size={16} weight="duotone" className="ic" color="var(--amber2)" />
        <span>Hidden Reasons</span>
        <span className="faint">/</span>
        <b>{pageName}</b>
      </div>

      <div className="sp" />

      {/* Bell / Alert menu */}
      <div style={{ position: 'relative' }}>
        <button
          className="iconbtn"
          onClick={() => setAlertsOpen(!alertsOpen)}
          title="Alerts"
          style={{ background: 'transparent', border: 'none', cursor: 'pointer', position: 'relative' }}
        >
          <Bell size={17} weight="duotone" className="ic" />
          {hasAlerts && (
            <span
              style={{
                position: 'absolute',
                top: '6px',
                right: '6px',
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                background: '#F85149',
                boxShadow: '0 0 6px rgba(248,81,73,0.8)',
              }}
            />
          )}
        </button>

        {alertsOpen && (
          <div
            style={{
              position: 'absolute',
              top: '42px',
              right: 0,
              width: '320px',
              background: 'var(--s1)',
              borderRadius: '12px',
              boxShadow: '0 0 0 1px var(--line2), 0 20px 40px rgba(0,0,0,0.7)',
              padding: '12px',
              zIndex: 100,
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
                borderBottom: '1px solid var(--line)',
                fontSize: '13px',
                fontWeight: 600,
              }}
            >
              <span>Pipeline Alerts</span>
              <span style={{ fontSize: '11px', color: 'var(--tx3)' }}>{alerts.length}</span>
            </div>
            <div style={{ maxHeight: '240px', overflowY: 'auto', paddingTop: '8px' }}>
              {alerts.length === 0 ? (
                <div style={{ padding: '16px 0', textAlign: 'center', fontSize: '12px', color: 'var(--tx3)' }}>
                  No open alerts. All systems healthy.
                </div>
              ) : (
                alerts.slice(0, 5).map((a, i) => (
                  <a
                    key={i}
                    href={a.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                      padding: '8px 0',
                      borderBottom: '1px solid var(--line)',
                      textDecoration: 'none',
                      color: 'inherit',
                    }}
                  >
                    <span style={{ fontSize: '12.5px', color: 'var(--tx)', fontWeight: 500 }}>
                      {a.title || a.body || 'Alert'}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--tx3)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {a.at ? new Date(a.at).toLocaleString() : 'Recent'} <ArrowSquareOut size={10} />
                    </span>
                  </a>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* New Film CTA */}
      <a
        href={studio.links.newFilm()}
        target="_blank"
        rel="noopener noreferrer"
        className="btn pri"
        style={{ height: '34px', fontSize: '13px', textDecoration: 'none' }}
      >
        <Plus size={15} weight="bold" className="ic" />
        <span>New film</span>
      </a>
    </header>
  );
};
