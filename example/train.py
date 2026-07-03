import random
from pathlib import Path

from expfreeze.log_utils import clear_lock, log_params
from expfreeze.utils import dump_json


def main() -> None:
    clear_lock()
    metrics_path = Path(__file__).parent / "metrics.json"
    params = {"lr": 0.01, "a": 1}
    log_params(params)
    metrics = {"train": [0.1, 0.2, 0.3], "test": [0.9]}
    dump_json(metrics, metrics_path)


if __name__ == "__main__":
    main()
