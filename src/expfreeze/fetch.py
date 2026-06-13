import json
import subprocess
import tomllib
from typing import NamedTuple

from expfreeze.const import EXPFR_DIR, LOCK_PATH


class ExperimentData(NamedTuple):
    name: str
    metrics: dict[str, list[float]]


def get_saved_metrics() -> list[ExperimentData]:
    commits: list[str] = []

    for branch in get_git_branches():
        cur_commits_raw = subprocess.check_output(["git", "-C", str(EXPFR_DIR), "log", branch, "--format=format:%H"])
        commits.extend(cur_commits_raw.decode().splitlines())

    all_metrics: list[ExperimentData] = []
    for commit in commits:
        try:
            lock_raw = subprocess.check_output(["git", "-C", str(EXPFR_DIR), "show", f"{commit}:{LOCK_PATH.name}"])
        except Exception:
            continue
        metrics_path = tomllib.loads(lock_raw.decode()).get("metrics_path")
        if metrics_path is None:
            continue
        metrics_raw = subprocess.check_output(["git", "-C", str(EXPFR_DIR), "show", f"{commit}:{metrics_path}"])
        cur_metrics: dict[str, list[float]] = json.loads(metrics_raw.decode())

        commit_name = subprocess.check_output(
            ["git", "-C", str(EXPFR_DIR), "log", "-1", "--format=%s", commit]
        ).decode()
        all_metrics.append(ExperimentData(commit_name, metrics=cur_metrics))

    return all_metrics


def get_git_branches(remote: bool = False) -> list[str]:
    out = subprocess.check_output(["git", "branch"] + (["-r"] if remote else []))
    branches = [b.strip() for b in out.decode().splitlines()]
    return [b.removeprefix("* ") for b in branches if "HEAD detached at" not in b and "->" not in b]
