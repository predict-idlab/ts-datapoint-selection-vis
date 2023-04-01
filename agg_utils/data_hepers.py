"""Helper functions for loading data and getting paths to figures."""

import pandas as pd
from .path_conf import figure_root_dir


def get_data_path(data, n, n_out, aggregator, **kwargs):
    """Get the path to the data file for the given parameters."""
    return figure_root_dir / (
        f"data/{data}_{aggregator}_{n}"
        + (f"{('_' + str(n_out)) if aggregator != 'reference' else ''}" + ".parquet")
    )


def get_series(aggregator, data, n, n_out=None, **kwargs) -> pd.Series:
    """Get the (aggregated) series for the given parameters."""
    df = pd.read_parquet(get_data_path(data, n, n_out, aggregator, **kwargs))
    df = df.set_index(df.columns[0])
    return df.iloc[:, 0]


def get_png_path(
    toolkit,
    data,
    n,
    n_out,
    aggregator,
    line_width,
    line_shape,
    aa: bool = False,
    **kwargs,
):
    aa = "_aa" if aa else ""
    return figure_root_dir / (
        f"{toolkit}/{aggregator}_{data}_{n}"
        + f"{('_' + str(n_out)) if aggregator != 'reference' else ''}"
        + f"_ls={line_shape}_lw={line_width}{aa}.png"
    )
