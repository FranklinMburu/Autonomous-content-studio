import React from 'react';
import { ArrowRight, Play } from '@phosphor-icons/react';
import { useStudio } from '../context/StudioContext';
import { useItems } from '../lib/items';
import { CHANNELS } from '../lib/channels';

// The landing page's "one studio, four channels" section: live numbers and the newest real video of each channel.
export const Channels: React.FC = () => {
  const { navigate } = useStudio();
  const items = useItems();
  return (
    <section className="lch" id="channels">
      <div className="lch-in">
        <div className="eyebrow">One studio · four channels</div>
        <h2 className="lch-t">Every channel makes its own kind of video.<br /><span className="serif">You only decide.</span></h2>
        <p className="lch-p">Free AI finds what to make, makes it and checks it. Each video waits for one decision from you: approve or skip. Nothing is posted without you, and it costs $0.</p>
        <div className="lch-grid">
          {CHANNELS.filter(c => c.code !== 'BS').map(c => {
            const mine = items.filter(i => i.lane === c.code && i.video);
            const top = mine.find(i => i.poster) || mine[0];
            return (
              <button key={c.code} className="lch-c" style={{ ['--lc' as any]: c.color }} onClick={() => navigate(`/app/c/${c.code}`)}>
                <div className={`lch-v${top?.vertical ? ' v' : ''}`} style={top?.poster ? { backgroundImage: `url(${top.poster})` } : undefined}>
                  {top ? <span className="vplay"><Play size={14} weight="fill" /></span> : <span className="lch-soon">{c.status}</span>}
                </div>
                <div className="lch-b">
                  <span className="lane" style={{ ['--lc' as any]: c.color }}><i />{c.code}</span>
                  <b>{c.name}</b>
                  <span>{c.short}</span>
                  <em>{mine.length ? `${mine.length} made` : c.status}</em>
                </div>
              </button>
            );
          })}
        </div>
        <div className="lch-cta">
          <button className="btn pri" onClick={() => navigate('/app')}>Open the studio</button>
          <button className="lnk" onClick={() => navigate('/how-it-works')}>How it works <ArrowRight size={13} /></button>
        </div>
      </div>
    </section>
  );
};
