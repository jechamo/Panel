"""Test bootstrap: redirect the data directory to a temp path so tests
don't touch the developer's panel.db or master key."""

import os
import tempfile
from pathlib import Path

# Tests must point the app at a fresh temp dir BEFORE app imports anything
# from app.db. We do this here in conftest so it runs at session start.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="panel-tests-"))
os.environ["PANEL_TEST_DATA_DIR"] = str(_TMP_DIR)
