from __future__ import annotations

import argparse
from pathlib import Path

from vnengine.assets.catalog import AssetCatalog, AssetType
from vnengine.runtime import Game
from vnengine.project_runtime import ProjectRuntime
from vnengine.frontends.pygame import PygameFrontend


def _is_data_project(project: Path) -> bool:
    return (project / "project.json").is_file()


def _run_data_project(project: Path) -> None:
    frontend = PygameFrontend(title=project.name or "PyNovel Engine")
    frontend.open()
    runtime = ProjectRuntime(project, frontend=frontend)
    try:
        runtime.viewport = frontend.screen.get_rect()
        from vnengine.project_runner import ProjectRunner
        ProjectRunner(runtime, poll_events=frontend.events, present=frontend.present, target=frontend.screen, clock=frontend.tick).run()
    finally:
        frontend.close()


def main() -> None:
    parser = argparse.ArgumentParser(prog="pynovel", description="Run and inspect a PyNovel project")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run a project")
    run.add_argument("project", type=Path)
    assets = sub.add_parser("assets", help="inspect project assets")
    assets_sub = assets.add_subparsers(dest="assets_command", required=True)
    scan = assets_sub.add_parser("scan", help="scan and index project assets")
    scan.add_argument("project", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        if _is_data_project(args.project): _run_data_project(args.project)
        else: Game(args.project).run()
    elif args.command == "assets" and args.assets_command == "scan":
        catalog = AssetCatalog(args.project); entries = catalog.scan(); index_path = catalog.write_index()
        counts = {asset_type.value: len(catalog.by_type(asset_type)) for asset_type in AssetType}
        print(f"Indexed {len(entries)} assets")
        for asset_type, count in counts.items():
            if count: print(f"  {asset_type}: {count}")
        print(f"Index: {index_path}")


if __name__ == "__main__": main()
