"""Path configuration for the agg_utils package."""

import socket
from inspect import getsourcefile
from pathlib import Path

if socket.gethostname() == "gecko":
    # The path to the UCR Archive dataset
    ucr_archive_dir = Path("/media/m4_datasets/datasets/UCRArchive_2018")

    # The `datasets_dir` should have the `btc` folder which contains the following
    # btc
    # ├── BTC-2017min.csv
    # ├── BTC-2018min.csv
    # ├── BTC-2019min.csv
    # ├── BTC-2020min.csv
    # ├── BTC-2021min.csv
    # ├── BTC-Daily.csv
    # └── BTC-Hourly.csv
    dataset_dir = ucr_archive_dir.parent

    # The `figure_root` must be an (initially empty) directory which will be populated
    # with the following subdirectories:
    # tsagg_figs
    # ├── bokeh
    # ├── data
    # ├── matplotlib
    # ├── matplotlib_cairo
    # └── plotly
    figure_root_dir = Path("/media/tsagg_figs/")
else:
    raise ValueError(f"Unknown hostname: {socket.gethostname()}")


loc_data_dir = Path(getsourcefile(lambda: 0)).absolute().parent.parent / "loc_data"
