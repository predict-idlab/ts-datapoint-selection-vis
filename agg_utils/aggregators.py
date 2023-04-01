"""
Tweaked implementations of aggregators with the aim of more convenient Benchmarking
"""

import numpy as np
import pandas as pd
from plotly_resampler.aggregation import AbstractSeriesAggregator


class M4Aggregator(AbstractSeriesAggregator):
    """Aggregation method which selects the 4 M-s, i.e y-argmin, y-argmax, x-argmin, and
    x-argmax per bin.

    .. note::
        When `n_out` is 4 * the canvas its pixel widht it should create a pixel-perfect
        visualization w.r.t. the raw data.

    """

    def __init__(self, interleave_gaps: bool = True, nan_position: str = "end"):
        """
        Parameters
        ----------
        interleave_gaps: bool, optional
            Whether None values should be added when there are gaps / irregularly
            sampled data. A quantile-based approach is used to determine the gaps /
            irregularly sampled data. By default, True.
        nan_position: str, optional
            Indicates where nans must be placed when gaps are detected. \n
            If ``'end'``, the first point after a gap will be replaced with a
            nan-value \n
            If ``'begin'``, the last point before a gap will be replaced with a
            nan-value \n
            If ``'both'``, both the encompassing gap datapoints are replaced with
            nan-values \n
            .. note::
                This parameter only has an effect when ``interleave_gaps`` is set
                to *True*.
        """
        # this downsampler supports all pd.Series dtypes
        super().__init__(interleave_gaps, nan_position)

    def _aggregate(self, s: pd.Series, n_out: int) -> pd.Series:
        assert n_out % 4 == 0, "n_out must be a multiple of 4"

        s_i = (
            s.index.view("int64")
            if s.index.dtype.type in (np.datetime64, pd.Timestamp)
            else s.index
        )

        # Thanks to the `linspace` the data is evenly distributed over the index-range
        # The searchsorted function returns the index positions
        bins = np.searchsorted(s_i, np.linspace(s_i[0], s_i[-1], n_out // 4 + 1))
        bins[-1] = len(s_i)
        bins = np.unique(bins)
        # print(bins)
        # print(s.iloc[bins].index)

        rel_idxs = []
        for lower, upper in zip(bins, bins[1:]):
            slice = s.iloc[lower:upper]
            if not len(slice):
                continue

            # calculate the min(idx), argmin(slice), argmax(slice), max(idx)
            rel_idxs.append(slice.index[0])
            rel_idxs.append(slice.idxmin())
            rel_idxs.append(slice.idxmax())
            rel_idxs.append(slice.index[-1])

        # NOTE: we do not use the np.unique so that all indices are retained
        return s.loc[sorted(rel_idxs)]
