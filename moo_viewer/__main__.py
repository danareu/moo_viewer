"""Allow `python -m moo_viewer` or the `moo-viewer` CLI entry point."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    app = Path(__file__).parent.parent / "app.py"
    sys.exit(subprocess.call(["streamlit", "run", str(app)] + sys.argv[1:]))


if __name__ == "__main__":
    main()
