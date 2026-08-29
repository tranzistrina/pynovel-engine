from vnengine.core.rng import DeterministicRNG


def test_same_seed_produces_same_sequence():
    a = DeterministicRNG(42)
    b = DeterministicRNG(42)
    assert [a.randint(1, 100) for _ in range(8)] == [b.randint(1, 100) for _ in range(8)]


def test_rng_state_round_trip_continues_sequence():
    rng = DeterministicRNG(123)
    rng.randint(1, 100)
    payload = rng.serialize()
    expected = [rng.randint(1, 100) for _ in range(5)]

    restored = DeterministicRNG(999)
    restored.deserialize(payload)
    assert [restored.randint(1, 100) for _ in range(5)] == expected


def test_chance_validates_probability():
    rng = DeterministicRNG(1)
    assert rng.chance(0.0) is False
    assert rng.chance(1.0) is True
    for value in (-0.1, 1.1):
        try:
            rng.chance(value)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid probability was accepted")
