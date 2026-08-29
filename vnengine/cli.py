from __future__ import annotations
import argparse
from vnengine.runtime import Game

def main():
    ap = argparse.ArgumentParser(description="Run a PyNovel game")
    ap.add_argument("project", nargs="?", default="examples/demo")
    args = ap.parse_args()
    Game(args.project).run()

if __name__ == "__main__": main()
