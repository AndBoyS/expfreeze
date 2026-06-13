from typing import Any

from expfreeze.const import LOCK_PATH
from expfreeze.utils import dump_toml, load_toml


def clear_lock() -> None:
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()


def log_params(params: dict[str, Any]) -> None:
    lock = load_toml(LOCK_PATH) if LOCK_PATH.exists() else {}
    all_params = lock.get("params", {})
    all_params.update(params)
    lock["params"] = all_params
    dump_toml(lock, LOCK_PATH)
