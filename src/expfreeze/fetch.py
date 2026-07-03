import json
import subprocess
import tomllib
from typing import NamedTuple

from scmrepo.fs import GitFileSystem

from expfreeze.const import LOCK_NAME, REPO_DIR, Refs


class ExpData(NamedTuple):
    name: str
    metrics: dict[str, list[float]]


class ExpCommit(NamedTuple):
    rev: str
    name: str


def get_all_exps() -> list[ExpCommit]:
    commits_raw = subprocess.check_output(
        ["git", "for-each-ref", "--format=%(objectname) %(refname)", f"{Refs.EXPS_PREFIX}*"]
    )
    exps: list[ExpCommit] = []
    for c in commits_raw.decode().splitlines():
        rev, name = c.split()
        exps.append(ExpCommit(rev=rev, name=name))
    return exps


def get_saved_metrics() -> list[ExpData]:
    all_metrics: list[ExpData] = []
    for exp in get_all_exps():
        fs = GitFileSystem(str(REPO_DIR), rev=exp.rev)
        try:
            lock_raw = fs.read_text(str(LOCK_NAME))
            assert isinstance(lock_raw, str)
            metrics_path: str | None = tomllib.loads(lock_raw).get("metrics_path")
            if metrics_path is None:
                continue
            cur_metrics: dict[str, list[float]] = json.loads(fs.read_text(metrics_path))
        except Exception:
            continue

        all_metrics.append(ExpData(exp.name, metrics=cur_metrics))

    return all_metrics
