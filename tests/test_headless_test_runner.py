from pathlib import Path

from vnengine.test_runner import HeadlessTestRunner, TestCase


def test_headless_runner_returns_machine_readable_result():
    project = Path(__file__).parents[1] / "examples" / "data"
    result = HeadlessTestRunner(project).run([TestCase("bootstrap", frames=1, expected_scene="map")])
    assert result["total"] == 1
    assert "results" in result
    assert result["results"][0]["name"] == "bootstrap"
