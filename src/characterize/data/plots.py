import pandas as pd
import plotly.graph_objects as go

from characterize.data.descriptor import ColumnarDescriptor


def render(data_descriptor: ColumnarDescriptor, df: pd.DataFrame) -> None:
    """Render a plotly SPA given extracted columnar semantics."""
    traces = []
    for signal in data_descriptor.columns:
        traces.append(
            go.Scatter(
                name=signal,
                x=df.index,
                y=df[signal],
            )
        )

    fig = go.Figure(data=traces)
    fig.show()

    return
