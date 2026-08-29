from __future__ import annotations
import sys
from pathlib import Path
from vnengine.runtime import Game

if __name__=='__main__':
    project=Path(sys.argv[1]) if len(sys.argv)>1 else Path('examples/demo')
    Game(project).run()
