from vnengine.performance import FixedTimestep, FrameCache, Profiler


def test_fixed_timestep_accumulates_and_bounds_steps():
    clock = FixedTimestep(step=0.1, max_steps=2)
    assert clock.advance(0.25) == 2
    assert 0.0 <= clock.accumulator <= 0.1
    clock.reset()
    assert clock.advance(0.05) == 0
    assert clock.advance(0.05) == 1


def test_frame_cache_is_bounded_lru():
    cache = FrameCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3


def test_profiler_is_noop_when_disabled():
    profiler = Profiler(False)
    with profiler.measure("update"):
        pass
    profiler.record("render", 1.0)
    assert profiler.snapshot() == {}


def test_profiler_collects_when_enabled():
    profiler = Profiler(True)
    with profiler.measure("update"):
        pass
    profiler.record("update", 0.001)
    sample = profiler.snapshot()["update"]
    assert sample["calls"] == 2
    assert sample["elapsed"] >= 0.001
    assert sample["average"] >= 0.0
