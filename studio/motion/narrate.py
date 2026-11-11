"""The channel's locked voice (channels/te/channel.json "voice"): Kokoro + the shared word-timing code in
studio/voice.py, then only the gentle EQ Franklin approved. Restores the shared defaults afterwards."""
import shutil, subprocess


def narrate(script, out_dir, voice_cfg):
    from .. import voice
    keep = (voice.GAP_LINE, voice.GAP_BEAT, voice.LEAD_IN, voice.TAIL, voice.TRIM_TAIL)
    s = dict(script, voice=voice_cfg["voice"], speed=voice_cfg["speed"])
    pace = voice_cfg["pace"]   # all five values come from the channel file, never from the shared defaults
    try:
        voice.GAP_LINE, voice.GAP_BEAT = pace["gap_line"], pace["gap_beat"]
        voice.LEAD_IN, voice.TAIL, voice.TRIM_TAIL = pace["lead_in"], pace["tail"], pace["trim_tail"]
        raw, out = out_dir / "voice_raw.wav", out_dir / "voice.wav"
        timing = voice.narrate(s, raw, out_dir / "timing.json")
    finally:
        voice.GAP_LINE, voice.GAP_BEAT, voice.LEAD_IN, voice.TAIL, voice.TRIM_TAIL = keep
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "aresample=48000," + voice_cfg["eq"], str(out)], check=True)
        raw.unlink()
    else:
        raw.replace(out)
    return timing
