import json
import random
import subprocess
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import tomli_w

from src.const import REPO_DIR


def load_json(path: str | Path, **kwargs: Any) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f, **kwargs)


def dump_json(
    obj: Any,
    path: str | Path,
    **kwargs: Any,
) -> None:
    ensure_ascii: bool = kwargs.pop("ensure_ascii", False)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=ensure_ascii, **kwargs)


def load_toml(path: str | Path, **kwargs: Any) -> Any:
    with open(path, "rb") as f:
        return tomllib.load(f, **kwargs)


def dump_toml(obj: Mapping[str, Any], path: str | Path, **kwargs: Any) -> None:
    with open(path, "wb") as f:
        tomli_w.dump(obj, f)


def get_random_words(n: int) -> str:
    noun_list = (REPO_DIR / "assets" / "nouns.txt").read_text().splitlines()
    return "-".join(random.choices(noun_list, k=n))


def is_git_ignored(p: Path, repo_dir: Path) -> bool:
    p = p.relative_to(repo_dir)
    args = ["git", "check-ignore", "-v", str(p)]
    out = subprocess.run(args, check=False, capture_output=True, text=True)
    if out.returncode and not out.stderr:
        return False
    if not out.returncode:
        return True
    raise subprocess.CalledProcessError(out.returncode, " ".join(args), stderr=out.stderr)
