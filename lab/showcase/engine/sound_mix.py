"""Music bed + effects for the showcase videos, using the studio's own synthesiser (studio/motion/sound.py),
then the studio's mix (voice on top, music ducked, effects under, -14 LUFS).
usage: python3 sound_mix.py <ep> <video_no_audio.mp4> <voice.wav> <timing.json> <out.mp4>"""
import sys, json, types, re, subprocess
sys.modules.setdefault('soundfile', types.ModuleType('soundfile'))        # sound.py imports it; we write wavs with scipy
sys.path.insert(0, '/home/claude/autonomous-content-studio')
import numpy as np
from scipy.io import wavfile
from studio.motion import sound

ep, video, voice, timing_p, out = sys.argv[1:6]
tm = json.load(open(timing_p)); words = tm['words']; dur = tm['duration'] + 1.4
norm = lambda s: re.sub(r"[^a-z0-9']", '', s.lower())
def T(w, n=1):
    c = 0
    for x in words:
        if norm(x['w']) == norm(w):
            c += 1
            if c == n: return x['start']
    return None
if ep == 'n1x':
    sec = {'groove_from': T('today'), 'kick_from': T('twenty'), 'break_from': T('but') - .05, 'break_to': T('gaming') - .05, 'calm_from': T('catch') - .05, 'end_from': T('next')}
    cues = [('pop', T('words')), ('whoosh', T('leave')), ('slam', T('october')), ('swoosh_big', T('today')), ('impact', T('center')), ('whoosh', T('waits')), ('zip', T('answer')),
            ('swoosh_big', T('back')), ('thump', T('lag')), ('blip', T('subscription')), ('whoosh', T('private')), ('impact', T("nvidia's")), ('riser', T('inside')),
            ('slam', T('twenty')), ('slam', T('six')), ('impact', T('petaflop')), ('riser', T('million')), ('thump', T('memory')), ('whoosh', T('gaming')),
            ('zip', T('here')), ('ding', T('pool')), ('thump', T('says')), ('swoosh_big', T('catch')), ('click', T('prism')), ('slam', T('starts')),
            ('whoosh', T('six', 2)), ('pop', T('cloud')), ('ding', T('here', 2))]
    cfg = {'bpm': 110, 'key': 'Am', 'kit': 'synth'}
else:
    sec = {'groove_from': T('more'), 'kick_from': T('laid'), 'break_from': T('so') - .05, 'break_to': T('real') - .05, 'calm_from': T('next') - .05, 'end_from': T('remember')}
    cues = [('pop', T('sent')), ('whoosh', T('space')), ('swoosh_big', T('down')), ('impact', T('bottom')), ('slam', T('more')), ('riser', T('laid')), ('impact', T('forty')),
            ('whoosh', T('deep')), ('zip', T('inside')), ('blip', T('flashes')), ('thump', T('shark')), ('slam', T('zero')), ('impact', T('anchors')), ('thump', T('around')),
            ('swoosh_big', T('only')), ('whoosh', T('drop')), ('riser', T('haul')), ('impact', T('daylight')), ('slam', T('quarter')), ('whoosh', T('next')), ('ding', T('arrives')), ('pop', T('remember'))]
    cfg = {'bpm': 104, 'key': 'Dm', 'kit': 'keys'}
cues = [{'kind': k, 't': t} for k, t in cues if t is not None]
seed = 7 if ep == 'n1x' else 11
m = sound.music(sec, dur, cfg, seed); s = sound.effects(cues, dur, seed)
wavfile.write(f'/tmp/{ep}_music.wav', sound.SR, m.astype(np.float32)); wavfile.write(f'/tmp/{ep}_sfx.wav', sound.SR, s.astype(np.float32))
sound.mix(video, voice, f'/tmp/{ep}_music.wav', f'/tmp/{ep}_sfx.wav', out)
print('mixed', out)
