import pytest

from musictool.chord import SpecificChord
from musictool.progression import Progression


@pytest.fixture
def four_chords():
    a = SpecificChord.random()
    b = SpecificChord.random()
    c = SpecificChord.random()
    d = SpecificChord.random()
    return a, b, c, d


@pytest.fixture
def progression4():
    a = SpecificChord.from_str('C1_E1_G1')
    b = SpecificChord.from_str('D1_F1_A1')
    c = SpecificChord.from_str('E1_G1_B1')
    d = SpecificChord.from_str('F1_A1_C2')
    return Progression([a, b, c, d])


def test_validation():
    with pytest.raises(TypeError):
        Progression([0, 1, 2])
    Progression([SpecificChord.random(), SpecificChord.random()])


def test_list_like(four_chords):
    a, b, c, d = four_chords
    p = Progression([a, b, c])
    assert len(p) == 3
    assert p[0] == a
    assert p == [a, b, c]
    e = [a, b, c, d]
    p.append(d)
    assert p == e
    assert Progression(x for x in [a, b, c, d]) == [a, b, c, d]


def test_all(progression4):
    def check(x, y): return x[0] < y[0]
    assert progression4.all([check])
    assert progression4.all_not([lambda x, y: not check(x, y)])


def test_distance(progression4):
    assert progression4.distance == 30


def test_transpose_unique_key(four_chords):
    a, b, c, d = four_chords
    d_ = SpecificChord(frozenset((d.notes_ascending[0] + 12,) + d.notes_ascending[1:]))
    p0 = Progression([a, b, c, d])
    p1 = Progression([a, b, c, d_])
    p2 = Progression(SpecificChord(frozenset(n + 12 for n in chord.notes)) for chord in p0)
    p3 = Progression(SpecificChord(frozenset(n + 1 for n in chord.notes)) for chord in p0)
    assert p0.transpose_unique_key() != p1.transpose_unique_key()
    assert p0.transpose_unique_key() == p2.transpose_unique_key()
    assert p0.transpose_unique_key() != p3.transpose_unique_key()
    assert p0.transpose_unique_key(origin_name=False) == p3.transpose_unique_key(origin_name=False)


def test_add_transpose():
    p0 = Progression([
        SpecificChord.from_str('G2_B2_e3'),
        SpecificChord.from_str('A2_C3_E3'),
        SpecificChord.from_str('B2_D3_f3'),
        SpecificChord.from_str('C3_E3_G3'),
    ])
    p1 = Progression([
        SpecificChord.from_str('C0_E0_a0'),
        SpecificChord.from_str('D0_F0_A0'),
        SpecificChord.from_str('E0_G0_B0'),
        SpecificChord.from_str('F0_A0_C1'),
    ])
    assert p0 + -31 == p1
    with pytest.raises(TypeError): p0 + [1]
    assert p0.transpose_to_note() == p1