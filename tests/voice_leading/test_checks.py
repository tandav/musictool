import pytest

from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.voice_leading import checks


def test_have_parallel_interval():
    # fifths
    a = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}))
    b = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 6)}))
    c = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    d = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('B', 5)}))
    h = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    i = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 6)}))
    j = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 7)}))

    assert checks.have_parallel_interval(a, b, 7)
    assert checks.have_parallel_interval(a, h, 7)
    assert checks.have_parallel_interval(i, j, 7)
    assert not checks.have_parallel_interval(a, c, 7)
    assert not checks.have_parallel_interval(a, d, 7)

    # octaves
    e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('C', 6)}))
    f = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('D', 6)}))
    g = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('E', 6)}))
    assert checks.have_parallel_interval(e, f, 0)
    assert not checks.have_parallel_interval(g, f, 0)


def test_have_hidden_parallel():
    a = SpecificChord(frozenset({SpecificNote('E', 5), SpecificNote('G', 5), SpecificNote('C', 6)}))
    b = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('F', 6)}))
    c = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('G', 5), SpecificNote('C', 6)}))
    d = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 6)}))
    e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('B', 5)}))
    f = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('D', 7)}))
    g = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('F', 5)}))
    h = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    i = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 6)}))
    assert checks.have_hidden_parallel(a, b, 0)
    assert checks.have_hidden_parallel(e, f, 0)
    assert checks.have_hidden_parallel(g, h, 7)
    assert checks.have_hidden_parallel(g, i, 7)
    assert not checks.have_hidden_parallel(c, b, 0)
    assert not checks.have_hidden_parallel(c, d, 0)


def test_have_voice_overlap():
    a = SpecificChord(frozenset({SpecificNote('E', 3), SpecificNote('E', 5), SpecificNote('G', 5), SpecificNote('B', 5)}))
    b = SpecificChord(frozenset({SpecificNote('A', 3), SpecificNote('C', 4), SpecificNote('E', 4), SpecificNote('A', 4)}))
    assert checks.have_voice_overlap(a, b)


@pytest.mark.parametrize('chord_str, max_interval, expected', (
    ('C1_d2', 12, True),
    ('C1_C2', 12, False),
    ('C1_d1', 1, False),
    ('C1_D1', 1, True),
    ('B0_C1', 2, False),
    ('B0_d1', 2, False),
    ('B0_D1', 2, True),
))
def test_large_spacing(chord_str, max_interval, expected):
    assert checks.large_spacing(SpecificChord.from_str(chord_str), max_interval) == expected