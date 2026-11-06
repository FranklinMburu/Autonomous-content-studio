import React from 'react';

interface MarkProps {
  size?: number;
  className?: string;
}

export const Mark: React.FC<MarkProps> = ({ size = 26, className = '' }) => {
  const id = `mg${size}`;
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" className={`mark ${className}`} style={{ flexShrink: 0 }}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#FFC861" />
          <stop offset="0.55" stopColor="#F5A524" />
          <stop offset="1" stopColor="#E0661B" />
        </linearGradient>
      </defs>
      <circle cx="32" cy="32" r="27" fill="none" stroke={`url(#${id})`} strokeWidth="5" />
      <path d="M32 13 C40 24 44 30 44 37 a12 12 0 0 1 -24 0 C20 30 24 24 32 13 Z" fill={`url(#${id})`} />
      <path d="M29 33 L39 38.5 L29 44 Z" fill="#0A0C14" />
    </svg>
  );
};
