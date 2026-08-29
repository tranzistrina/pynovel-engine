from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description='Build a standalone PyNovel game')
    p.add_argument('project',type=Path); p.add_argument('--name',default='MyNovel'); args=p.parse_args()
    try: import PyInstaller  # noqa: F401
    except ImportError: raise SystemExit('PyInstaller is required: python -m pip install pyinstaller')
    root=Path(__file__).resolve().parents[1]
    subprocess.check_call([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--name',args.name,'--windowed','--onedir','--paths',str(root),str(root/'tools/launcher.py')])
if __name__=='__main__':main()
