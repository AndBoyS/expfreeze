from collections import defaultdict

from dash import Dash, Input, Output, dcc, html

from src.const import EXPFR_DIR, LOCK_PATH
from src.fetch import ExperimentData, get_saved_metrics
from src.utils import load_toml

app = Dash()

ONE_SECOND = 1000
app.layout = [
    html.H1(children="Title of Dash App", style={"textAlign": "center"}),
    html.Div(id="container"),
    dcc.Interval(
        id="interval-component",
        interval=ONE_SECOND * 1,
        n_intervals=0,
    ),
]

LAST_LOCK_TIME: str | None = None
LAST_METRICS: list[ExperimentData] | None = None


@app.callback(
    Output("container", "children"),
    [Input("interval-component", "n_intervals")],
)
def update_graph(n: int) -> html.Div:
    global LAST_LOCK_TIME, LAST_METRICS  # noqa: PLW0603
    lock = load_toml(EXPFR_DIR / LOCK_PATH.name)
    lock_write_time: str = lock["write_time"]
    if lock_write_time == LAST_LOCK_TIME and LAST_METRICS is not None:
        all_metrics = LAST_METRICS
    else:
        all_metrics = get_saved_metrics()
        LAST_METRICS = all_metrics
        LAST_LOCK_TIME = lock_write_time
    metric_type_dict: dict[str, list[tuple[str, list[float]]]] = defaultdict(list)
    for exp in all_metrics:
        for name, cur_nums in exp.metrics.items():
            metric_type_dict[name].append((exp.name, cur_nums))

    graphs: list[dcc.Graph] = []

    for name, exp in metric_type_dict.items():
        graphs.append(
            dcc.Graph(
                id=f"graph-{name}",
                figure={
                    "data": [
                        {"x": len(cur_metrics), "y": cur_metrics, "name": exp_name} for exp_name, cur_metrics in exp
                    ],
                    "layout": {
                        "title": {"text": name},
                    },
                },
            )
        )
    return html.Div(graphs)


if __name__ == "__main__":
    app.run(debug=True)
