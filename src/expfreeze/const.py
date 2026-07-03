from pathlib import Path

REPO_DIR = Path(__file__).parents[2]
LOCK_NAME = "expfreeze.lock"
LOCK_PATH = REPO_DIR / LOCK_NAME


class Refs:
    EXPS_PREFIX = "refs/exps/"
    LAST_EXP = "refs/exps_special/LAST_EXP"
