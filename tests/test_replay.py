from __future__ import annotations

from vnengine.replay import ReplayPlayer, ReplaySession


def test_replay_roundtrip_is_deterministic():
    replay = ReplaySession(metadata={"name": "smoke"})
    replay.record(1 / 60, ["left"])
    replay.record(0.25, [])
    payload = replay.to_dict()
    restored = ReplaySession.from_dict(payload)
    assert restored.to_dict() == payload
    assert restored.digest() == replay.digest()


def test_replay_player_is_sequential_and_resettable():
    replay = ReplaySession()
    replay.record(0.1, ["a"])
    replay.record(0.2, ["b"])
    player = ReplayPlayer(replay)
    assert player.remaining() == 2
    assert player.next_frame().events == ("a",)
    assert player.remaining() == 1
    assert player.next_frame().events == ("b",)
    assert player.finished
    assert player.next_frame() is None
    player.reset()
    assert player.next_frame().dt == 0.1
