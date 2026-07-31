"""
One-off script that pulls real data from the World Bank Open Data API and
writes it to backend/data/raw/*.csv, which is committed to the repo so the
app runs immediately after cloning.

Usage (from backend/):
    python scripts/fetch_data.py
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data.cache import refresh  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    summary = refresh()
    print(f"Done: {summary}")
