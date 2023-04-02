import itertools
import os
import sys

import pandas as pd
import plotly.express as px
from tqdm.auto import tqdm

sys.path.append("..")
from agg_utils.fig_construction import construct_bokeh_fig
from agg_utils.path_conf import figure_root_dir, loc_data_dir

# read in the agg data csv from `0.2_create_agg_data.ipynb` and construct the
# corresponding dicts which will be used by the visualization toolkits to operate upon
df_agg_data = pd.read_csv(loc_data_dir / "agg_data.csv")


n_out_mask = pd.isna(df_agg_data.n_out)


def read_set_index_first_col(pqt_path) -> pd.Series:
    df = pd.read_parquet(pqt_path)
    df = df.set_index(df.columns[0], drop=True)
    assert len(df.columns) == 1
    return df.iloc[:, 0]


ref_data_dict = {
    f"{r.data}_{r.aggregator}_{r.n}": read_set_index_first_col(r.path)
    for _, r in tqdm(
        df_agg_data[n_out_mask].iterrows(), total=sum(n_out_mask), ncols=80, ascii=True
    )
}

agg_data_dict = {
    f"{r.data}_{r.aggregator}_{r.n}_{int(r.n_out)}": read_set_index_first_col(r.path)
    for _, r in tqdm(
        df_agg_data[~n_out_mask].iterrows(),
        total=sum(~n_out_mask),
        ncols=80,
        ascii=True,
    )
}


line_width_grid = [1, 2, 3, 4]
drawstyle_grid = ["default", "steps-mid"]
bokeh_save_dir = figure_root_dir / "bokeh"
if not bokeh_save_dir.exists():
    os.makedirs(bokeh_save_dir)
bokeh_vis_grid = line_width_grid, drawstyle_grid


def wrap_create_bokeh_figs(k: str):
    s_name, aggregator, n, n_out = k.split("_")
    agg_data = agg_data_dict[k]
    ref_data = ref_data_dict[f"{s_name}_reference_{n}"]
    xlim = (ref_data.index[0], ref_data.index[-1])
    ylim = (ref_data.min(), ref_data.max())
    for line_width, drawstyle in list(itertools.product(*bokeh_vis_grid)):
        save_name = (
            str(bokeh_save_dir)
            + f"/{aggregator}_{s_name}_{n}_{int(n_out)}_ls={drawstyle}_lw={line_width}"
        )
        construct_bokeh_fig(
            agg_data.index,
            agg_data.values.ravel(),
            save_path=save_name + ".png",
            xlim=xlim,
            ylim=ylim,
            line_width=line_width,
            line_shape=drawstyle,
        )


ks = sorted(list(agg_data_dict.keys()))
for t in tqdm(ks, ncols=80, ascii=True):
    wrap_create_bokeh_figs(t)
