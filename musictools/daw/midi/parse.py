import functools
from enum import Enum
from enum import auto
from pathlib import Path
from typing import Sequence
from typing import Union
from typing import get_args

PathLike = Union[str, Path]

import mido
import numpy as np

from ... import config
from ...note import SpecificNote
from ..vst import VST


class State(Enum):
    TODO = auto()
    IN_PROGRESS = auto()
    DONE = auto()


class NoteSound:
    def __init__(
        self,
        absolute_i: int,
        sample_on: int,
        sample_off: int,
        vst: VST,
    ):
        """
        TODO:
            - maybe remove some variables (which can be expressed via other)
            - maybe add some logic for  not to use sustain envelope when self.stop_decay > self.sample_off
                - now it does automatically (empty masks)

        ns_ means number of samples
        stop_xxx means sample where xxx is no more playing
        """
        self.note = SpecificNote.from_absolute_i(absolute_i)
        self.sample_on = sample_on
        self.sample_off = sample_off
        self.ns = sample_off - sample_on

        self.ns_release = int(vst.adsr(self.note).release * config.sample_rate)
        self.stop_release = sample_off + self.ns_release  # actual sample when note is off (including release)

        self.ns_attack = min(int(vst.adsr(self.note).attack * config.sample_rate), self.ns)
        self.ns_decay_original = max(int(vst.adsr(self.note).decay * config.sample_rate), 1)  # prevent from equal to zero
        self.ns_decay = min(self.ns_decay_original, self.ns - self.ns_attack)
        self.ns_sustain = self.ns - self.ns_attack - self.ns_decay

        self.stop_attack = self.sample_on + self.ns_attack
        self.stop_decay = self.stop_attack + self.ns_decay
        # self.stop_sustain = self.sample_off  # do the math

        # todo: use difference, not ranges
        self.range_attack = np.arange(self.sample_on, self.stop_attack)
        self.range_decay = np.arange(self.stop_attack, self.stop_decay)
        self.range_sustain = np.arange(self.stop_decay, self.sample_off)
        self.range_release = np.arange(self.sample_off, self.stop_release)

        self.attack_envelope = np.linspace(0, 1, self.ns_attack, endpoint=False, dtype='float32')
        # if decay is longer than note then actual sustain is higher than vst.adsr(self.note).sustain (do the math)
        se = max((vst.adsr(self.note).sustain - 1) * (self.ns - self.ns_attack) / self.ns_decay_original + 1, vst.adsr(self.note).sustain)  # sustain extra
        self.decay_envelope = np.linspace(1, se, self.ns_decay, endpoint=False, dtype='float32')
        self.release_envelope = np.linspace(se, 0, self.ns_release, endpoint=False, dtype='float32')

        self.ns_rendered = 0
        self.vst = vst
        self.key = self.note, self.sample_on, self.stop_release
        self.state = State.TODO

    def render(self, chunk, samples=None):
        self.state = State.IN_PROGRESS
        if samples is None:
            samples = np.arange(len(chunk))
        mask = (self.sample_on <= samples) & (samples < self.stop_release)
        ns_to_render = np.count_nonzero(mask)

        mask_attack = (self.sample_on <= samples) & (samples < self.stop_attack)
        mask_decay = (self.stop_attack <= samples) & (samples < self.stop_decay)
        mask_sustain = (self.stop_decay <= samples) & (samples < self.sample_off)
        mask_release = (self.sample_off <= samples) & (samples < self.stop_release)

        wave = self.vst(self.ns_rendered, ns_to_render, self.note)

        wave[mask_attack[mask]] *= self.attack_envelope[(samples[0] <= self.range_attack) & (self.range_attack <= samples[-1])]
        wave[mask_decay[mask]] *= self.decay_envelope[(samples[0] <= self.range_decay) & (self.range_decay <= samples[-1])]
        wave[mask_sustain[mask]] *= self.vst.adsr(self.note).sustain
        wave[mask_release[mask]] *= self.release_envelope[(samples[0] <= self.range_release) & (self.range_release <= samples[-1])]
        chunk[mask] += wave
        self.ns_rendered += ns_to_render

        if samples is None or self.stop_release + self.ns_release <= samples[-1]:
            self.state = State.DONE

    def reset(self):
        self.ns_rendered = 0

    def __hash__(self): return hash(self.key)
    def __eq__(self, other): return self.key == other.key


class ParsedMidi:
    def __init__(self, midi: mido.MidiFile, vst: Union[VST, Sequence[VST]]):
        """
        :param midi: Midi with one or many channels
        :param vst:
        """

        ticks_set = set()
        notes = []
        numerator = None

        if len(midi.tracks) == 1:
            vst = [vst]

        for track, vst_ in zip(midi.tracks, vst):
            ticks, seconds, n_samples = 0, 0., 0
            note_buffer = dict()
            for message in track:
                # print(track, message)
                if message.type == 'time_signature':
                    if message.denominator != 4:
                        raise NotImplementedError('denominators other than 4 are not supported')
                    numerator = message.numerator
                    ticks_per_bar = numerator * midi.ticks_per_beat

                ticks += message.time
                d_seconds = mido.tick2second(message.time, midi.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))
                seconds += d_seconds
                n_samples += int(config.sample_rate * d_seconds)
                if message.type == 'note_on':
                    note_buffer[message.note] = n_samples
                elif message.type == 'note_off':
                    # print(n_samples)
                    notes.append(NoteSound(message.note, note_buffer.pop(message.note), n_samples, vst=vst_))
            ticks_set.add(self.round_ticks_to_bar(ticks, ticks_per_bar))

        if not len(ticks_set) == 1:
            raise ValueError('number of ticks rounded to bar should be equal for all midi tracks/channels')
        ticks = next(iter(ticks_set))

        self.n_samples = int(config.sample_rate * mido.tick2second(ticks, midi.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute)))
        self.numerator = numerator
        self.notes = notes

    def round_ticks_to_bar(self, ticks, ticks_per_bar):
        div, mod = divmod(ticks, ticks_per_bar)
        if mod:
            ticks += ticks_per_bar - mod
        return ticks

    def reset(self):
        for note in self.notes:
            note.reset()

    # @classmethod
    # @functools.singledispatchmethod # TODO
    # def from_many(cls, midis: Union[Sequence[PathLike], Sequence[mido.MidiFile]], vst: Sequence[VST]):
    #     if isinstance(Sequence)


    @classmethod
    def from_files(cls, midi_files: Union[PathLike, Sequence[PathLike]], vst: Union[VST, Sequence[VST]]):
        if isinstance(midi_files, get_args(PathLike)):  # get_args is shitty but works
            assert isinstance(vst, VST)
            midi = mido.MidiFile(config.midi_folder + midi_files, type=0)
            return cls(midi, vst)
        return cls.from_many([mido.MidiFile(config.midi_folder + f, type=0) for f in midi_files], vst)

    @classmethod
    def from_many(cls, midi_objects: Sequence[mido.MidiFile], vst: Sequence[VST]):
        """
        convert many midi files into one with multiple channels
        """
        assert len(midi_objects) == len(vst)
        midi = mido.MidiFile(type=1)

        numerators, denominators = set(), set()
        ticks_per_beat_s = dict()

        for i, track_midi in enumerate(midi_objects):
            # print(f)
            track = mido.MidiTrack()
            time_signature_parsed = False
            ticks_per_beat_s[i] = track_midi.ticks_per_beat

            for message in track_midi.tracks[0]:
                # print(message)
                if message.type == 'track_name':
                    message.name = Path(track_midi.filename).stem if track_midi.filename is not None else f'track_{i}'
                elif message.type == 'time_signature':
                    numerators.add(message.numerator)
                    denominators.add(message.denominator)
                    if time_signature_parsed:
                        continue
                    else:
                        time_signature_parsed = True
                elif message.type == 'note_on' or message.type == 'note_off':
                    message.channel = i
                track.append(message)
            if not time_signature_parsed:
                raise ValueError(f'input midi {i} {track_midi.filename} must have time_signature message')

            midi.tracks.append(track)

        if not len(set(ticks_per_beat_s.values())) == 1:
            raise NotImplementedError(f'cant merge midi files with different ticks_per_beat: {ticks_per_beat_s}')

        midi.ticks_per_beat = next(iter(ticks_per_beat_s.values()))  # in merged file must be as in input files

        if not (len(numerators) == len(denominators) == 1):
            raise NotImplementedError(f'cant merge midi files with different or without time_signatures (numerator {numerators} and denominator {denominators})')

        return cls(midi, vst)

    @classmethod
    def from_file(cls, midi_file, vst: VST):
        return cls(mido.MidiFile(config.midi_folder + midi_file, type=1), vst)