import os
import sys
from pathlib import Path

# Make sure signal_analysis.py (and db.py) can be imported directly,
# the same way callbacks.py and app.py import them.
DASH_SRC = Path(__file__).resolve().parents[1] / "src" / "dash"
sys.path.insert(0, str(DASH_SRC))

# db.py raises if DB_URL is unset. Tests never hit the database (they exercise
# pure functions on in-memory DataFrames), so a placeholder should be enough to satisfy
# the import-time check without requiring a real Postgres instance.
os.environ.setdefault("DB_URL", "postgresql://test:test@localhost:5432/testdb")
