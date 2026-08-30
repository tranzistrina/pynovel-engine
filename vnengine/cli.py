from __future__ import annotations

import argparse
import json
from pathlib import Path

from vnengine.assets.catalog import AssetCatalog, AssetType
from vnengine.runtime import Game
from vnengine.project_runtime import ProjectRuntime
from vnengine.frontends.pygame import PygameFrontend
from vnengine.agent import AIAgentInterface
from vnengine.dsl import GameDSL, DSLParseError
from vnengine.test_runner import HeadlessTestRunner
from vnengine.replay import ReplaySession


def _is_data_project(project: Path) -> bool:
    return (project / "project.json").is_file()


def _run_data_project(project: Path) -> None:
    frontend = PygameFrontend(title=project.name or "PyNovel Engine")
    frontend.open(); runtime = ProjectRuntime(project, frontend=frontend)
    try:
        runtime.viewport = frontend.screen.get_rect()
        from vnengine.project_runner import ProjectRunner
        ProjectRunner(runtime, poll_events=frontend.events, present=frontend.present, target=frontend.screen, clock=frontend.tick).run()
    finally: frontend.close()


def _load_operations(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle: data = json.load(handle)
    if not isinstance(data, list): raise SystemExit("Operations file must contain a JSON array")
    return data


def _agent_command(args: argparse.Namespace) -> None:
    agent = AIAgentInterface(args.project)
    if args.agent_action == "inspect": result = agent.inspect()
    elif args.agent_action == "validate": result = agent.validate()
    elif args.agent_action == "diagnose": result = agent.diagnose()
    elif args.agent_action == "schema": result = agent.command_schema()
    elif args.agent_action in {"plan", "dry-run", "apply"}:
        operations = _load_operations(args.operations); result = agent.plan(operations) if args.agent_action == "plan" else agent.execute(operations, dry_run=args.agent_action == "dry-run", save=not args.no_save)
    else: raise SystemExit(f"Unknown agent action: {args.agent_action}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def _dsl_command(args: argparse.Namespace) -> None:
    source = args.source.read_text(encoding="utf-8")
    try:
        parsed = GameDSL().parse(source) if args.dsl_action == "validate" else None
        if args.dsl_action == "validate": print(json.dumps({"valid": True, "project": parsed.project, "scenes": sorted(parsed.scenes)}, ensure_ascii=False, indent=2))
        else: print(json.dumps(GameDSL().compile(source, args.output), ensure_ascii=False, indent=2))
    except DSLParseError as exc:
        print(json.dumps({"valid": False, "error": {"code": "dsl_parse_error", "line": exc.line, "message": str(exc)}}, ensure_ascii=False, indent=2)); raise SystemExit(2) from exc


def _test_command(args: argparse.Namespace) -> int:
    runner = HeadlessTestRunner(args.project)
    cases = runner.load_cases(args.spec) if args.spec else runner.load_cases(args.project / "tests.json") if (args.project / "tests.json").is_file() else runner.load_cases(Path(__file__).parents[1] / "tests" / "specs" / "smoke.json")
    result = runner.run(cases); print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result["failed"] == 0 else 1


def _replay_command(args: argparse.Namespace) -> int:
    with args.replay.open("r", encoding="utf-8") as handle: session = ReplaySession.from_dict(json.load(handle))
    if args.replay_action == "inspect":
        result = {"version": 1, "frames": len(session.frames), "duration": sum(frame.dt for frame in session.frames), "digest": session.digest(), "metadata": session.metadata}
    elif args.replay_action == "digest":
        result = {"digest": session.digest(), "frames": len(session.frames)}
    else:
        raise SystemExit(f"Unknown replay action: {args.replay_action}")
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="pynovel", description="Run and inspect a PyNovel project")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run a project"); run.add_argument("project", type=Path)
    test = sub.add_parser("test", help="run deterministic headless project tests"); test.add_argument("project", type=Path); test.add_argument("--spec", type=Path, default=None)
    replay = sub.add_parser("replay", help="inspect deterministic replay recordings")
    replay_sub = replay.add_subparsers(dest="replay_action", required=True)
    for action in ("inspect", "digest"):
        command = replay_sub.add_parser(action); command.add_argument("replay", type=Path)
    dsl = sub.add_parser("dsl", help="compile or validate declarative game files")
    dsl_sub = dsl.add_subparsers(dest="dsl_action", required=True)
    compile_cmd = dsl_sub.add_parser("compile", help="compile a .game file into project files"); compile_cmd.add_argument("source", type=Path); compile_cmd.add_argument("output", type=Path)
    validate_cmd = dsl_sub.add_parser("validate", help="validate a .game file"); validate_cmd.add_argument("source", type=Path)
    assets = sub.add_parser("assets", help="inspect project assets")
    assets_sub = assets.add_subparsers(dest="assets_command", required=True)
    scan = assets_sub.add_parser("scan", help="scan and index project assets"); scan.add_argument("project", type=Path)
    agent = sub.add_parser("agent", help="AI-friendly project authoring and diagnostics")
    agent_sub = agent.add_subparsers(dest="agent_action", required=True)
    for action in ("inspect", "validate", "diagnose", "schema"):
        command = agent_sub.add_parser(action); command.add_argument("project", type=Path)
    for action in ("plan", "dry-run", "apply"):
        command = agent_sub.add_parser(action); command.add_argument("project", type=Path); command.add_argument("operations", type=Path); command.add_argument("--no-save", action="store_true")
    args = parser.parse_args()
    if args.command == "run":
        if _is_data_project(args.project): _run_data_project(args.project)
        else: Game(args.project).run()
    elif args.command == "test": raise SystemExit(_test_command(args))
    elif args.command == "replay": raise SystemExit(_replay_command(args))
    elif args.command == "dsl": _dsl_command(args)
    elif args.command == "assets" and args.assets_command == "scan":
        catalog = AssetCatalog(args.project); entries = catalog.scan(); index_path = catalog.write_index(); counts = {asset_type.value: len(catalog.by_type(asset_type)) for asset_type in AssetType}
        print(f"Indexed {len(entries)} assets")
        for asset_type, count in counts.items():
            if count: print(f"  {asset_type}: {count}")
        print(f"Index: {index_path}")
    elif args.command == "agent": _agent_command(args)


if __name__ == "__main__": main()
