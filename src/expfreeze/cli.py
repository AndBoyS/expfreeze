import datetime
import subprocess
from typing import Any

import click

from expfreeze.const import LOCK_PATH, REPO_DIR, Refs
from expfreeze.utils import dump_toml, get_random_words, load_toml


@click.command()
@click.argument("path")
@click.option("--name", default=None, help="Name of the experiment")
@click.option("--run", "run_exp", flag_value=True, default=False, help="Run the pipeline")
def save_exp(path: str, name: str | None = None, run_exp: bool = False) -> None:
    pipe_info: dict[str, Any] = load_toml(path)
    if run_exp:
        subprocess.run(pipe_info["run_cmd"], check=True, shell=True)
    metrics_path = REPO_DIR / pipe_info["metrics_path"]

    lock: dict[str, Any] = {}
    if LOCK_PATH.exists():
        lock = load_toml(LOCK_PATH)
    lock["write_time"] = datetime.datetime.now().strftime("%H:%M:%S")
    lock["run_cmd"] = pipe_info["run_cmd"]
    lock["metrics_path"] = pipe_info["metrics_path"]

    dump_toml(lock, LOCK_PATH)
    stash_res = subprocess.run(["git", "stash", "--staged"], capture_output=True, check=False).stdout.decode()

    # TODO: check for already existing name
    if name is None:
        name = get_random_words(n=3)

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "add", "--force", LOCK_PATH], check=True)
    subprocess.run(["git", "add", "--force", metrics_path], check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f"{name}\n\nTo replicate: {pipe_info['run_cmd']}\nMetrics: {metrics_path}",
        ],
        check=True,
    )
    subprocess.run(["git", "update-ref", f"{Refs.EXPS_PREFIX}{name}", "HEAD"], check=True)
    subprocess.run(["git", "reset", "--mixed", "HEAD~1"], check=True)

    if stash_res:
        subprocess.run(["git", "stash", "pop", "--index"], check=True)


if __name__ == "__main__":
    save_exp([str(REPO_DIR / "example/pipe.toml")])
