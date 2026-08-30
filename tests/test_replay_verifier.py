from vnengine.replay import ReplaySession
from vnengine.replay_verifier import ReplayVerifier


class FakeRuntime:
    def __init__(self):
        self.running = False
        self.value = 0

    def start(self, **kwargs):
        self.running = True

    def update(self, dt):
        self.value += int(dt * 10)

    def handle_input(self, event):
        if event == "inc":
            self.value += 1
            return True
        return False

    def render(self, target=None):
        return None

    def save_state(self):
        return {"value": self.value}

    def load_state(self, state):
        self.value = state["value"]

    def stop(self):
        self.running = False


def test_replay_verifier_reports_first_difference():
    session = ReplaySession()
    session.record(0.1, ("inc",))
    session.record(0.2)
    result = ReplayVerifier(FakeRuntime).run(session, expected_snapshots=[{"value": 2}, {"value": 4}])
    assert result.passed
    assert result.frames_checked == 2
    assert result.first_difference is None


def test_replay_verifier_finds_first_difference_path():
    session = ReplaySession()
    session.record(0.1, ("inc",))
    session.record(0.2)
    result = ReplayVerifier(FakeRuntime).run(session, expected_snapshots=[{"value": 99}, {"value": 4}])
    assert not result.passed
    assert result.first_difference is not None
    assert result.first_difference.frame == 0
    assert result.first_difference.path == "frames[0].state.value"
    assert result.first_difference.expected == 99
    assert result.first_difference.actual == 2
