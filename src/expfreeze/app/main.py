from collections import defaultdict
from typing import Any, TypeAlias

from dash import Dash, Input, Output, State, dcc, html

from expfreeze.const import EXPFR_DIR, LOCK_PATH
from expfreeze.fetch import ExperimentData, get_saved_metrics
from expfreeze.utils import load_toml

app = Dash()

ONE_SECOND = 1000
app.layout = [
    html.H1(children="Title of Dash App", style={"textAlign": "center"}),
    html.Div(id="container"),
    dcc.Store("metrics-store", storage_type="session"),
    dcc.Store("lock-time-store", storage_type="session"),
    dcc.Interval(
        id="interval-component",
        interval=ONE_SECOND * 1,
        n_intervals=0,
    ),
]


class TypedGraph(dcc.Graph):
    figure: dict[str, Any]


@app.callback(
    Output("container", "children"),
    Output("metrics-store", "data"),
    Output("lock-time-store", "data"),
    [
        Input("interval-component", "n_intervals"),
        State("container", "children"),
        State("metrics-store", "data"),
        State("lock-time-store", "data"),
    ],
)
def update_graph(
    n: int, graphs_div: dict[str, Any] | None, last_metrics: list[ExperimentData] | None, last_lock_time: str | None
) -> tuple[html.Div | dict[str, Any], list[ExperimentData], str]:
    lock = load_toml(EXPFR_DIR / LOCK_PATH.name)
    lock_write_time: str = lock["write_time"]
    if lock_write_time == last_lock_time and last_metrics is not None:
        assert graphs_div is not None
        return graphs_div, last_metrics, last_lock_time

    all_metrics = get_saved_metrics()
    ExpName: TypeAlias = str
    metric_type_dict: dict[str, list[tuple[ExpName, list[float]]]] = defaultdict(list)
    for exp in all_metrics:
        for name, cur_nums in exp.metrics.items():
            metric_type_dict[name].append((exp.name, cur_nums))

    if graphs_div is None:
        graphs: list[TypedGraph] = []

        for name, exp_data in metric_type_dict.items():
            graphs.append(
                TypedGraph(
                    id=f"graph-{name}",
                    figure={
                        "data": [
                            {"x": len(cur_metrics), "y": cur_metrics, "name": exp_name}
                            for exp_name, cur_metrics in exp_data
                        ],
                        "layout": {
                            "title": {"text": name},
                        },
                    },
                )
            )

        return html.Div(graphs), all_metrics, lock_write_time
    del graphs
    graphs_data: list[dict[str, Any]] = graphs_div["props"]["children"]

    metric_to_graph: dict[str, dict[str, Any]] = {
        g["props"]["layouе"]["layout"]["title"]["text"]: g for g in graphs_data
    }
    for metric_name, exp_name_line in metric_type_dict.items():
        metric_graph = metric_to_graph.get(metric_name)
        if metric_graph is not None:
            exp_name_to_line: dict[str, dict[str, Any]] = {line["name"]: line for line in metric_graph.figure["data"]}
            for exp_name, exp_line in exp_name_line:
                exp_line_data = {"x": len(exp_line), "y": exp_line}
                prev_line_data = exp_name_to_line.get(exp_name)
                if prev_line_data is None:
                    metric_graph.figure["data"].append(exp_line_data)
                elif prev_line_data["y"] != exp_line:
                    prev_line_data.clear()
                    prev_line_data.update(exp_line_data)
        else:
            metric_to_graph[metric_name] = TypedGraph(
                id=f"graph-{metric_name}",
                figure={
                    "data": [
                        {"x": len(exp_line), "y": exp_line, "name": exp_name} for exp_name, exp_line in exp_name_line
                    ],
                    "layout": {
                        "title": {"text": metric_name},
                    },
                },
            )

    return html.Div(list(metric_to_graph.values())), all_metrics, lock_write_time


if __name__ == "__main__":
    app.run(debug=True)
