from datetime import timedelta
import srt

def seconds_to_td(s):
    return timedelta(seconds=float(s))

def build_even_srt(text_sentences, total_seconds):
    """Split sentences evenly across total_seconds, return SRT string."""
    n = max(1, len(text_sentences))
    dur = total_seconds / n
    subs = []
    t = 0.0
    for i, line in enumerate(text_sentences, start=1):
        start = seconds_to_td(t)
        end = seconds_to_td(t + dur)
        subs.append(srt.Subtitle(index=i, start=start, end=end, content=line))
        t += dur
    return srt.compose(subs)
