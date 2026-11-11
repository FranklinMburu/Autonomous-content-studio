// Which globe the home page shows. Change ONE word and commit (GitHub web editor is fine): the site redeploys itself.
//   'earth' = the real-Earth film globe (11 Nov 2026)      'dots' = the dotted globe (before)
export const GLOBE_DEFAULT: 'earth' | 'dots' = 'earth';

// The small "Globe: Earth | Dots" switch in the bottom-left corner of the hero, for showing people both.
// false = hide it (visitors then see only GLOBE_DEFAULT; the ?globe= links below still work).
export const SHOW_GLOBE_SWITCH = true;

// Share links (one visit, nothing saved):  <site>/?globe=earth   <site>/?globe=dots
// Keyboard: press G on the home page to flip. The switch and G remember the choice in that browser only.
