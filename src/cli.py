import os
import shutil
import subprocess
from pathlib import Path

import click

from src.const import EXPFR_DIR, REPO_DIR
from src.utils import get_random_words, is_git_ignored, load_toml


@click.command()
@click.argument("path")
@click.option("--name", default=None, help="Name of the experiment")
def save_exp(path: str, name: str | None = None) -> None:
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
    metrics_path = REPO_DIR / (d["pipeline"]["metrics_path"])
    shutil.copy(metrics_path, EXPFR_DIR / "expreeze_metrics.json")

    os.chdir(EXPFR_DIR)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f'"{name}"'], check=True)


if __name__ == "__main__":
    save_exp()
