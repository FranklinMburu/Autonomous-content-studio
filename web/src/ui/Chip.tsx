import React from 'react';

export interface ChipProps {
  status?: string;
  label?: string;
  className?: string;
  style?: React.CSSProperties;
}

export const Chip: React.FC<ChipProps> = ({ status, label, className = '', style }) => {
  let chipClass = 'chip';
  let chipLabel = label;

  switch (status) {
    case 'ready':
      chipClass += ' ok';
      chipLabel = chipLabel || 'Ready to upload';
      break;
    case 'uploaded':
      chipClass += ' ok';
      chipLabel = chipLabel || 'Uploaded';
      break;
    case 'finished':
    case 'done':
    case 'success':
      chipClass += ' ok';
      chipLabel = chipLabel || (status === 'success' ? 'Done' : 'Finished');
      break;
    case 'review':
      chipClass += ' rev';
      chipLabel = chipLabel || 'Review';
      break;
    case 'polish':
      chipClass += ' rev';
      chipLabel = chipLabel || 'Needs your polish';
      break;
    case 'draft':
      chipLabel = chipLabel || 'Draft';
      break;
    case 'running':
    case 'making':
      chipClass += ' run';
      chipLabel = chipLabel || 'Making';
      break;
    case 'queued':
      chipClass += ' run';
      chipLabel = chipLabel || 'Queued';
      break;
    case 'failure':
    case 'failed':
      chipClass += ' bad';
      chipLabel = chipLabel || 'Failed';
      break;
    case 'cancelled':
      chipClass += ' bad';
      chipLabel = chipLabel || 'Cancelled';
      break;
    case 'ok':
      chipClass += ' ok';
      break;
    case 'rev':
      chipClass += ' rev';
      break;
    case 'bad':
      chipClass += ' bad';
      break;
    case 'run':
      chipClass += ' run';
      break;
    default:
      break;
  }

  const hasDot = status === 'running' || status === 'making' || status === 'queued' || chipClass.includes('run');

  return (
    <span className={`${chipClass} ${className}`.trim()} style={style}>
      {hasDot && <span className="dot" />}
      {chipLabel || label}
    </span>
  );
};
