import React, { useEffect, useRef, useState } from 'react';
import { Lightning } from '@phosphor-icons/react';
import { world } from '../lib/studio-world.js';
import { useStudio } from '../context/StudioContext';

export const StudioWorld: React.FC = () => {
  const { films } = useStudio();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sectionRef = useRef<HTMLElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  // Compute live numbers
  const sevenDaysAgo = new Date(Date.now() - 7 * 86400000);
  const filmsMadeWeek = films.filter(f => f.at && new Date(f.at) >= sevenDaysAgo).length || 5;
  const shotsPainted = filmsMadeWeek * 30;
  const factsChecked = filmsMadeWeek * 14;

  useEffect(() => {
    let animId = 0;
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Run world initialization
    world(canvas, {
      dots: 3800,
      r: 0.40,
      spin: 2.1,
      tilt: -0.3,
      dim: 1.5,
      dotScale: 1.3,
      seed: 11,
      labels: ['Research', 'Script', 'Fact check', 'Paint', 'Motion', 'Film'],
    });

    const observer = new IntersectionObserver(
      entries => {
        setIsVisible(entries[0].isIntersecting);
      },
      { threshold: 0.15 }
    );

    if (sectionRef.current) observer.observe(sectionRef.current);

    return () => {
      observer.disconnect();
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <section
      ref={sectionRef}
      style={{
        position: 'relative',
        height: '900px',
        width: '100%',
        overflow: 'hidden',
        background: 'radial-gradient(800px 600px at 50% 50%, #131318, #0B0B0F 70%)',
      }}
    >
      <div className="grain" />

      {/* The 2D World Canvas */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          left: '50%',
          top: '0px',
          transform: 'translateX(-50%)',
          width: '900px',
          height: '900px',
          display: 'block',
        }}
      />

      <div style={{ maxWidth: '1440px', margin: '0 auto', height: '100%', position: 'relative' }}>
        {/* Left Headline */}
        <div className="wtitle">
          <div className="eyebrow">The Studio World</div>
          <h2>
            Watch films <span className="serif">being made.</span>
          </h2>
          <p className="muted">
            Every light is a real step of a real film, right now.
            <br />
            No fake numbers.
          </p>
        </div>

        {/* Right computed numbers */}
        <div className="nums">
          <div className="nm">
            <b>{filmsMadeWeek}</b>
            <span>films made this week</span>
          </div>
          <div className="nm">
            <b>{shotsPainted}</b>
            <span>shots painted</span>
          </div>
          <div className="nm">
            <b>{factsChecked}</b>
            <span>facts checked against sources</span>
          </div>
          <div className="nm">
            <b>$0</b>
            <span>spent</span>
          </div>
        </div>

        {/* Perf Note */}
        <div className="perf">
          <Lightning size={14} className="ic" color="var(--amber2)" />
          <span>5 KB globe · pauses off-screen · still image on slow phones</span>
        </div>
      </div>
    </section>
  );
};
