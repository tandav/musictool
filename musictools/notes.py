import random

from musictools.note import Note
from musictools import chromatic
from musictools import config


'''
Notes
    NotesWithRoot
        Scale
        Chord
'''




class Notes:
    intervals_to_name: dict = {}
    name_to_intervals: dict = {}

    def __init__(
        self,
        notes: frozenset[str | Note],
        root: str | Note | None = None,
    ):
        """
        chord is an unordered set of notes
        root:
            root note of a chord (to distinguish between inversions_
            root note is optional, some chord can has no root
            chord w/o root has no intervals
        """

        if isinstance(next(iter(notes)), str):
            notes = frozenset(Note(note) for note in notes)

        if isinstance(root, str):
            root = Note(root)

        self.notes = notes
        self.root = root
        self.key = self.notes, self.root
        self.notes_ascending = chromatic.sort_notes(self.notes, start=self.root)
        self.str_chord = ''.join(note.name for note in self.notes_ascending)

        if root is not None:
            if root not in notes:
                raise ValueError('root note should be one of the chord notes')

            self.intervals = frozenset(note - root for note in notes - {root})
            self.name = self.__class__.intervals_to_name.get(self.intervals)

    @property
    def rootless(self): return Notes(self.notes)

    @classmethod
    def from_name(cls, root: str | Note, name: str):
        if isinstance(root, str):
            root = Note(root)
        notes = frozenset(root + interval for interval in cls.name_to_intervals[name]) | {root}
        return cls(notes, root)

    @classmethod
    def from_intervals(cls, root: str | Note, intervals: frozenset):
        if isinstance(root, str):
            root = Note(root)
        return cls(frozenset(root + interval for interval in intervals) | {root}, root)

    @classmethod
    def random(cls, n_notes=None):
        if n_notes is None:
            n_notes = random.randint(2, 5)
        notes = frozenset(random.sample(config.chromatic_notes, n_notes))
        return cls(notes)

    @classmethod
    def from_str(cls, string: str):
        notes, _, root = string.partition('/')
        root = Note(root) if root else None
        notes = frozenset(Note(note) for note in notes)
        return cls(notes, root)

    def add_note(self, note: Note, steps: int):
        notes = self.notes_ascending
        if type(note) is Note:
            return notes[(notes.index(note) + steps) % len(notes)]
        else:
            raise TypeError

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __len__(self): return len(self.notes)
    def __contains__(self, item): return item in self.notes
    # def __str__(self): return ''.join(note.name for note in self.notes)

    # def to_piano_image(self, base64=False):
    #     return Piano(chord=self)._repr_svg_()

    def __repr__(self):
        _ = self.str_chord
        if self.root is not None:
            _ += f'/{self.root.name}'
        return _

    # async def play(self, seconds=1):
    #     await SpecificChord(
    #         notes=frozenset(SpecificNote(note) for note in self.notes),
    #         root=self.root,
    #     ).play(seconds)
    #     notes_to_play = self.specific_notes
    #
    #     if bass:
    #         notes_to_play = itertools.chain(notes_to_play, [Note(self.root.name, octave=self.root.octave + bass)])
    #
    #     tasks = tuple(note.play(seconds) for note in notes_to_play)
    #     await asyncio.gather(*tasks)

    # def _repr_html_(self):
    #     label = hasattr(self, 'label') and f"id={self.label!r}"or ''
    #     number = hasattr(self, 'number') and self.number or ''
    #
    #     return f'''
    #     <li class='card {self.name}' {label}>
    #     <a href='play_chord_{self.str_chord}'>
    #     <span class='card_header' ><h3>{number} {self.root} {self.name}</h3></span>
    #     <img src='{self.to_piano_image(base64=True)}' />
    #     </a>
    #     </li>
    #     '''

    # def __repr__(self):
    #     label = hasattr(self, 'label') and f"id={self.label!r}"or ''
    #     number = hasattr(self, 'number') and self.number or ''
    #
    #     return f'''
    #     <li class='card {self.name}' {label} onclick=play_chord('{str(self)}')>
    #     <span class='card_header' ><h3>{number} {self.root} {self.name}</h3></span>
    #     <img src='{self.to_piano_image(base64=True)}' />
    #     </li>
    #     '''

# class SpecificNotes: pass
