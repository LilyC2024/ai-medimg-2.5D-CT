"""Compatibility wrapper for the unified versioned case preparation CLI.
Use --series-dir and --output-dir; old threshold flags are no longer accepted.
"""

from prepare_case import main

if __name__ == "__main__":
    raise SystemExit(main())
