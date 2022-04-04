import itertools
from collections import Counter

import pytest

from musictool.util.sequence_builder import SequenceBuilder


def is_even(x):
    return x % 2 == 0


def identity(x):
    return x


def different_startswith(a: str, b: str) -> bool:
    return a[0] != b[0]


def equal_endswith(a: str, b: str) -> bool:
    return a[1] == b[1]


def even_odd_interchange(prev, curr):
    return is_even(prev) ^ is_even(curr)


def candidate_constraint(candidate: tuple[str, ...]) -> bool:
    return Counter(candidate)['A'] < 3


def options_callable_0(x):
    return [x + 1]


def options_callable_1(x):
    return [x + 1, x * 10]


@pytest.fixture
def options() -> tuple[int, ...]:
    return 0, 1, 2, 3


def test_length(options):
    assert all(len(seq) == 4 for seq in SequenceBuilder(4, options=(0, 1, 2), i_constraints={0: is_even}))


def test_first_constraint(options):
    assert all(is_even(seq[0]) for seq in SequenceBuilder(4, options=(0, 1, 2), i_constraints={0: is_even}))


def test_input_validation():
    with pytest.raises(ValueError): tuple(SequenceBuilder(5, options=(1, 1, 2)))


def test_prev_curr(options):
    for cycle in SequenceBuilder(5, options=options, curr_prev_constraint={-1: even_odd_interchange}, loop=True):
        assert even_odd_interchange(cycle[-1], cycle[0])
        for prev, curr in itertools.pairwise(cycle):
            assert even_odd_interchange(prev, curr)


def test_loop():
    assert all(
        different_startswith(seq[0], seq[-1]) and equal_endswith(seq[1], seq[-1])
        for seq in SequenceBuilder(
            4,
            options=('A0', 'A1', 'C0', 'D0', 'D1'),
            curr_prev_constraint={-1: different_startswith, -2: equal_endswith},
            loop=True,
        )
    )


@pytest.mark.parametrize('parallel', (False, True))
def test_prefix(options, parallel):
    prefix = options[:3]
    assert all(seq[:len(prefix)] == prefix for seq in SequenceBuilder(5, options=options, prefix=prefix, parallel=parallel))


@pytest.mark.parametrize('parallel', (False, True))
def test_unique(options, parallel):
    assert all(len(seq) == len(set(seq)) for seq in SequenceBuilder(4, options=options, unique_key=identity, parallel=parallel))
    assert any(len(seq) != len(set(seq)) for seq in SequenceBuilder(4, options=options, parallel=parallel))


@pytest.mark.parametrize('parallel', (False, True))
def test_candidate_constraint(parallel):
    assert all(
        candidate_constraint(seq)
        for seq in SequenceBuilder(
            n=4,
            options='AB',
            candidate_constraint=candidate_constraint,
            parallel=parallel,
        )
    )


@pytest.mark.parametrize('parallel', (False, True))
def test_options_kind_callable(parallel):
    assert set(SequenceBuilder(3, options_callable=options_callable_0, prefix=(0,), parallel=parallel)) == {(0, 1, 2)}
    assert set(SequenceBuilder(3, options_callable=options_callable_1, prefix=(0,), parallel=parallel)) == {(0, 1, 2), (0, 1, 10), (0, 0, 1), (0, 0, 0)}


@pytest.mark.parametrize('parallel', (False, True))
def test_options_i(parallel):
    options_i = [{1, 10}, {2, 20}, {3, 30}]
    assert all(
        all(item in options_i[i] for i, item in enumerate(seq))
        for seq in SequenceBuilder(3, options_i=options_i, parallel=parallel)
    )
    with pytest.raises(ValueError):
        SequenceBuilder(3, options_i=options_i[:2], parallel=parallel)


# def test_parallel():
#     options_0 = 0, 1, 2, 3, 4, 5, 6, 7, 8
#     a = SequenceBuilder(5, options=options_0, i_constraints={0: is_even})
#     b = SequenceBuilder(5, options=options_0, i_constraints={0: is_even}, parallel=True)
#     # assert tuple(a) == tuple(b)
#     assert frozenset(a) == frozenset(b)
#
#     options_1 = 'A0', 'A1', 'C0', 'D0', 'D1', 'G0'
#     a = SequenceBuilder(5, options=options_1, curr_prev_constraint={-1: different_startswith, -2: equal_endswith})
#     b = SequenceBuilder(5, options=options_1, curr_prev_constraint={-1: different_startswith, -2: equal_endswith}, parallel=True)
#     # assert tuple(a) == tuple(b)
#     assert frozenset(a) == frozenset(b)

def test_parallel():
    options_0 = 0, 1, 2, 3, 4
    a = SequenceBuilder(3, options=options_0, i_constraints={0: is_even})
    b = SequenceBuilder(3, options=options_0, i_constraints={0: is_even}, parallel=True)
    # assert tuple(a) == tuple(b)
    assert frozenset(a) == frozenset(b)

    options_1 = 'A0', 'A1', 'C0', 'D0', 'D1', 'G0'
    a = SequenceBuilder(5, options=options_1, curr_prev_constraint={-1: different_startswith, -2: equal_endswith})
    b = SequenceBuilder(5, options=options_1, curr_prev_constraint={-1: different_startswith, -2: equal_endswith}, parallel=True)
    # assert tuple(a) == tuple(b)
    assert frozenset(a) == frozenset(b)
