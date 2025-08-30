from pathlib import Path

from src.utils import dump_json


def main() -> None:
    metrics_path = Path(__file__).parent / "metrics.json"
    metrics = {"train": [0.1, 0.2, 0.3]}
    dump_json(metrics, metrics_path)


if __name__ == "__main__":
    main()
