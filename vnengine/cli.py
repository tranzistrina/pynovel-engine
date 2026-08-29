from __future__ import annotations
import argparse
from pathlib import Path
from vnengine.runtime import Game

def main():
    parser=argparse.ArgumentParser(prog='pynovel',description='Run a PyNovel game')
    sub=parser.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run'); run.add_argument('project',type=Path)
    args=parser.parse_args()
    if args.command=='run':Game(args.project).run()
if __name__=='__main__':main()
