import datetime
import shutil
import subprocess

import click

from src.const import EXPFR_DIR, LOCK_PATH, REPO_DIR
from src.utils import dump_toml, get_random_words, is_git_ignored, load_toml


@click.command()
@click.argument("path")
@click.option("--name", default=None, help="Name of the experiment")
def save_exp(path: str, name: str | None = None) -> None:
    if LOCK_PATH.exists():
        lock = load_toml(LOCK_PATH)
    lock["write_time"] = datetime.datetime.now().strftime("%H:%M:%S")
    dump_toml(lock, LOCK_PATH)

    if name is None:
        name = get_random_words(n=3)

    for p in EXPFR_DIR.glob("*"):
        if p.name == ".git":
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()

    for p in REPO_DIR.glob("*"):
        if p.name in [".git", EXPFR_DIR.name] or is_git_ignored(p, repo_dir=REPO_DIR):
            continue
        if p.is_dir():
            shutil.copytree(p, EXPFR_DIR / p.name)
        else:
            shutil.copyfile(p, EXPFR_DIR / p.name)

    d = load_toml(path)
    metrics_path: str = d["metrics_path"]

    subprocess.run(["git", "-C", str(EXPFR_DIR), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(EXPFR_DIR),
            "commit",
            "-m",
            f"{name}\n\nTo replicate: {d['run_cmd']}\nMetrics: {metrics_path}",
        ],
        check=True,
    )


if __name__ == "__main__":
    save_exp()
