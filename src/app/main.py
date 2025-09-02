from collections import defaultdict

from dash import Dash, Input, Output, dcc, html

from src.const import EXPFR_DIR, LOCK_PATH
from src.fetch import get_all_metrics
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
LAST_METRICS: list[dict[str, list[float]]] | None = None


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
        all_metrics = get_all_metrics()
        LAST_METRICS = all_metrics
        LAST_LOCK_TIME = lock_write_time
    metric_type_dict: dict[str, list[list[float]]] = defaultdict(list)
    for metrics in all_metrics:
        for name, cur_nums in metrics.items():
            metric_type_dict[name].append(cur_nums)

    graphs = []

    for name, metrics in metric_type_dict.items():
        graphs.append(
            dcc.Graph(
                id=f"graph-{name}",
                figure={
                    "data": [{"x": len(cur_metrics), "y": cur_metrics} for cur_metrics in metrics],
                    "layout": {
                        "title": {"text": name},
                    },
                },
            )
        )
    return html.Div(graphs)


if __name__ == "__main__":
    app.run(debug=True)
