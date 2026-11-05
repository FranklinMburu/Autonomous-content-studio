import React from 'react';
import { WarningCircle, House, FilmStrip } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const NotFoundView: React.FC = () => {
  const { navigate } = useStudio();

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="soonpage" style={{ alignItems: 'center', textAlign: 'center' }}>
        <div className="sic" style={{ margin: '0 auto' }}>
          <WarningCircle size={32} weight="duotone" color="var(--amber2)" />
        </div>
        <h1 className="st1">404</h1>
        <p className="sp1">This page doesn't exist.</p>
        <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
          <button className="btn pri" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <House size={16} />
            <span>Go to Landing</span>
          </button>
          <button className="btn sec" onClick={() => navigate('/app/films')} style={{ cursor: 'pointer' }}>
            <FilmStrip size={16} />
            <span>Go to Studio</span>
          </button>
        </div>
      </div>
    </div>
  );
};
