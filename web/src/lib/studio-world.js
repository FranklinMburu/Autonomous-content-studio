// The Studio World sphere (section 5, mockup 05_landing_studio_world). Copied EXACTLY from the approved mockup.
// Canvas 2D, no libraries. Usage: <canvas data-world='{...}'> is auto-initialised by the last line, or call world(canvas, opts).
// In React: call world(ref.current, opts) inside useEffect; pause it when the section is off-screen (IntersectionObserver).

function world(canvas, opt){
  const o = Object.assign({dots:1400, r:0.42, tilt:-0.35, spin:0.6, glow:'245,165,36', cool:'121,192,255', arcs:7, seed:3, dim:1}, opt||{});
  const dpr = 2, W = canvas.clientWidth, H = canvas.clientHeight;
  canvas.width = W*dpr; canvas.height = H*dpr;
  const c = canvas.getContext('2d'); c.scale(dpr,dpr);
  const R = Math.min(W,H)*o.r, cx = W/2, cy = H/2;
  let s = o.seed; const rnd = ()=> (s = (s*9301+49297)%233280)/233280;
  const pts=[]; const N=o.dots, ga=Math.PI*(3-Math.sqrt(5));
  for(let i=0;i<N;i++){ const y=1-(i/(N-1))*2, rr=Math.sqrt(1-y*y), th=ga*i; pts.push([Math.cos(th)*rr, y, Math.sin(th)*rr, rnd()]); }
  const rot=(p)=>{ let [x,y,z]=p; const a=o.spin, ca=Math.cos(a), sa=Math.sin(a); [x,z]=[x*ca+z*sa, -x*sa+z*ca];
    const b=o.tilt, cb=Math.cos(b), sb=Math.sin(b); [y,z]=[y*cb-z*sb, y*sb+z*cb]; return [x,y,z]; };
  // halo
  let g=c.createRadialGradient(cx,cy,R*0.6,cx,cy,R*1.55); g.addColorStop(0,`rgba(${o.glow},${0.10*o.dim})`); g.addColorStop(1,'rgba(0,0,0,0)');
  c.fillStyle=g; c.fillRect(0,0,W,H);
  g=c.createRadialGradient(cx-R*0.35,cy-R*0.4,R*0.1,cx,cy,R); g.addColorStop(0,`rgba(${o.cool},${0.10*o.dim})`); g.addColorStop(1,'rgba(10,12,20,0)');
  c.fillStyle=g; c.beginPath(); c.arc(cx,cy,R,0,7); c.fill();
  // dots
  const lit=[];
  for(const p of pts){ const [x,y,z]=rot(p); if(z< -0.15) continue; const a=(z+0.15)/1.15;
    const hot = p[3]>0.992; const warm = p[3]>0.90;
    c.fillStyle = hot? `rgba(${o.glow},${(0.95*a).toFixed(3)})` : warm? `rgba(${o.glow},${(0.45*a*o.dim).toFixed(3)})` : `rgba(200,210,235,${Math.min(0.75,0.34*a*o.dim).toFixed(3)})`;
    const rr = (hot? 2.4 : 1.15)*(o.dotScale||1); c.beginPath(); c.arc(cx+x*R, cy+y*R, rr*(0.6+0.4*a),0,7); c.fill();
    if(hot){ lit.push([cx+x*R, cy+y*R]); const gg=c.createRadialGradient(cx+x*R,cy+y*R,0,cx+x*R,cy+y*R,14); gg.addColorStop(0,`rgba(${o.glow},.45)`); gg.addColorStop(1,`rgba(${o.glow},0)`); c.fillStyle=gg; c.beginPath(); c.arc(cx+x*R,cy+y*R,14,0,7); c.fill(); }
  }
  // labelled path mode: pick well-spread front-facing lit points, connect them in order (the steps of one film)
  let pairs=[];
  if(o.labels){
    const front=[]; for(const p of pts){ const q=rot(p); if(q[2]>0.35) front.push([cx+q[0]*R, cy+q[1]*R, Math.atan2(q[1],q[0])]); }
    const n=o.labels.length, chosen=[];
    for(let i=0;i<n;i++){ const ang=-2.6+ i*(5.2/(n-1)); let best=null,bd=1e9;
      for(const f of front){ const rr=Math.hypot(f[0]-cx,f[1]-cy)/R; if(rr<0.35||rr>0.78) continue; const d=Math.abs(((f[2]-ang+Math.PI*3)%(Math.PI*2))-Math.PI); if(d<bd){bd=d;best=f;} }
      chosen.push(best); }
    lit.length=0; for(const c2 of chosen){ lit.push([c2[0],c2[1]]);
      const gg=c.createRadialGradient(c2[0],c2[1],0,c2[0],c2[1],18); gg.addColorStop(0,`rgba(${o.glow},.55)`); gg.addColorStop(1,`rgba(${o.glow},0)`); c.fillStyle=gg; c.beginPath(); c.arc(c2[0],c2[1],18,0,7); c.fill();
      c.fillStyle='rgba(255,226,170,1)'; c.beginPath(); c.arc(c2[0],c2[1],3,0,7); c.fill(); }
    for(let i=0;i<n-1;i++) pairs.push([lit[i],lit[i+1]]);
    const host=canvas.parentElement, box=canvas.getBoundingClientRect();
    o.labels.forEach((t,i)=>{ const d=document.createElement('div'); d.className='wl'; d.innerHTML=t;
      d.style.left=(box.left+lit[i][0]+12)+'px'; d.style.top=(box.top+lit[i][1]-14)+'px'; host.appendChild(d); });
  } else { for(let k=0;k<Math.min(o.arcs, lit.length-1);k++) pairs.push([lit[k], lit[(k*3+2)%lit.length]]); }
  for(const [a,b] of pairs){ const mx=(a[0]+b[0])/2, my=(a[1]+b[1])/2 - Math.hypot(b[0]-a[0],b[1]-a[1])*0.45;
    const lg=c.createLinearGradient(a[0],a[1],b[0],b[1]); lg.addColorStop(0,`rgba(${o.glow},0)`); lg.addColorStop(0.5,`rgba(${o.glow},.85)`); lg.addColorStop(1,`rgba(${o.cool},.15)`);
    c.strokeStyle=lg; c.lineWidth=1.3; c.beginPath(); c.moveTo(a[0],a[1]); c.quadraticCurveTo(mx,my,b[0],b[1]); c.stroke();
    // travelling spark
    const t=0.62; const sx=(1-t)*(1-t)*a[0]+2*(1-t)*t*mx+t*t*b[0], sy=(1-t)*(1-t)*a[1]+2*(1-t)*t*my+t*t*b[1];
    const sg=c.createRadialGradient(sx,sy,0,sx,sy,7); sg.addColorStop(0,'rgba(255,230,180,1)'); sg.addColorStop(1,`rgba(${o.glow},0)`); c.fillStyle=sg; c.beginPath(); c.arc(sx,sy,7,0,7); c.fill();
  }
  // rim / atmosphere: a warm sunrise along the top edge of the planet
  if(o.horizon){
    for(const [w,a] of [[60,0.10],[26,0.22],[8,0.5],[2,0.9]]){
      c.save(); c.shadowColor=`rgba(${o.glow},${a})`; c.shadowBlur=w; c.strokeStyle=`rgba(255,214,150,${a*0.8})`; c.lineWidth=w>20?2:1.4;
      c.beginPath(); c.arc(cx,cy,R,Math.PI*1.08,Math.PI*1.92); c.stroke(); c.restore(); }
  } else { c.strokeStyle=`rgba(255,255,255,${0.06*o.dim})`; c.lineWidth=1; c.beginPath(); c.arc(cx,cy,R,0,7); c.stroke(); }
}
document.querySelectorAll('canvas[data-world]').forEach(cv=>world(cv, JSON.parse(cv.dataset.world||'{}')));

export { world };
