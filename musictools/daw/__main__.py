import contextlib
import io

import pyaudio

from .. import config
from ..midi.parse import MidiTrack
from ..note import SpecificNote
from . import render
from . import vst


@contextlib.contextmanager
def audio_stream(fake=False):
    if fake:
        yield io.BytesIO()
        return
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)
    yield stream
    stream.stop_stream()
    stream.close()
    p.terminate()


def main() -> int:
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.001))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.001, decay=0.05, sustain=1, release=1))
    # synth = vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    synth = vst.Sampler(note_to_sample_path={
        SpecificNote('C', 3): config.kick,
        SpecificNote('e', 3): config.clap,
        SpecificNote('b', 3): config.hat,
    }, adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    track = MidiTrack.from_file(config.midi_file, vst=synth)

    with audio_stream(fake=False) as stream:
        for _ in range(4):
            # render.single(stream, track)
            render.chunked(stream, track)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
