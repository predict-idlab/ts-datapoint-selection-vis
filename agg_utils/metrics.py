"""Metrics to asess image quality of aggregated figures w.r.t. the reference figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.ndimage as ndi
from skimage.metrics import structural_similarity as ssim

# import scipy.signal as ss

from .data_hepers import get_png_path


def _get_or_conv_mask(img1, img2, win_size: int = 11) -> np.ndarray:
    """Return the OR convolution mask."""
    joined = (img1 + img2) > 0
    # ss.convolve2d(joined, np.ones((win_size, win_size)), mode="same") != 0
    # The above 2d conv is equivalent to applying the following 1d convs
    # which is ~15x faster than the 2d conv
    out = ndi.convolve1d(joined > 0, np.ones(win_size), axis=0, mode="reflect")
    out = ndi.convolve1d(out, np.ones(win_size), axis=1, mode="reflect") > 0
    return out


def _get_dssim_series(agg, ref, dim, or_conv_mask, **ssim_kwargs) -> pd.Series:
    """Compute the DSSIM and SSIM metrics."""
    # calculate the SSIM, OR convolution mask, and DSSIM
    ssim_kwgs = dict(win_size=11, full=True, gradient=False)
    ssim_kwgs.update(ssim_kwargs)

    # Compute the SSIM
    SSIM = ssim(ref[:, :, dim], agg[:, :, dim], **ssim_kwgs)[1]

    # Compute hte (masked) DSSIM, and mask the SSIM as well
    DSSIM = (1 - SSIM) / 2
    DSSIM_masked = DSSIM.ravel()[or_conv_mask.ravel()]
    SSIM_masked = SSIM.ravel()[or_conv_mask.ravel()]

    return pd.Series(
        index=["DSSIM", "DSSIM_masked", "SSIM", "SSIM_masked"],
        data=[
            np.mean(DSSIM),
            np.mean(DSSIM_masked),
            np.mean(SSIM),
            np.mean(SSIM_masked),
        ],
    )


def _get_mse_series(agg, ref, dim, or_conv_mask) -> pd.Series:
    """Compute the MSE, MAE, and pixel error margin metrics."""
    # Conpute the pixel wise MSE and MAE
    SE = ((agg[:, :, dim] - ref[:, :, dim])) ** 2
    # note: we cast the data to avoid rounding errors when computing the Pixel errors
    # which are derived from the MAE
    AE = np.abs((agg[:, :, dim] - ref[:, :, dim])).astype(int)

    MSE = np.mean(SE)
    MSE_masked = SE.ravel()[or_conv_mask.ravel()].mean()
    MAE = np.mean(AE)
    MAE_masked = AE.ravel()[or_conv_mask.ravel()].mean()

    return pd.Series(
        index=[
            "MSE",
            "MSE_masked",
            "MAE",
            "MAE_masked",
            "conv_mask_size",
            "pixel_errors",
            "pixel_errors_margin_10",
            "pixel_errors_margin_20",
            "pixel_errors_margin_30",
            "pixel_errors_margin_50",
            "pixel_errors_margin_75",
            "pixel_errors_margin_100",
        ],
        data=[
            MSE,
            MSE_masked,
            MAE,
            MAE_masked,
            or_conv_mask.sum(),
            (AE != 0).sum(),
            (AE > 10).sum(),
            (AE > 20).sum(),
            (AE > 30).sum(),
            (AE > 50).sum(),
            (AE > 75).sum(),
            (AE > 100).sum(),
        ],
    )


def compute_dssim_plotly(
    agg_path: str | Path, ref_dict, mse: bool, **ssim_kwargs
) -> pd.Series:
    """Compute the DSSIM, MSE, and MAE for a Plotly figure.

    More specifically, this function computes the DSSIM for a reference figure with
    a line width of 1 and the same line width as the original figure.

    .. NOTE::
        This method can also be used for the `Bokeh` toolit

    parameters
    ----------
    idx_r : pd.Series
        a row of the aggregation dataframe
    ref_dict : dict
        a dictionary of reference images, with the path as key and the image as value
    ssim_kwargs : dict
        keyword arguments for the skimage.metrics.structural_similarity function

    returns
    -------
    pd.Series
        a row of the aggregation dataframe with the MSSIM and DSSIM values added
        More specifically, this function adds the following columns:
        - DSSIM_ref_lw=1
        - DSSIM_masked_ref_lw=1
        - DSSIM_same_lw
        - DSSIM_masked_same_lw
        - SSIM_ref_lw=1
        - SSIM_masked_ref_lw=1
        - SSIM_same_lw
        - SSIM_masked_same_lw

    """
    agg_path: Path = Path(agg_path)
    toolkit: str = agg_path.parent.name
    splits = (agg_path.name).split(".")[0].split("_")
    aggregator, data, n, n_out, ls, lw = splits[:6]
    # AA is an additional (last) name field for the matplotlib toolkit
    aa = len(splits) == 7
    ls = ls[3:]
    lw = lw[3:]

    # fmt: off
    reference_path_lw1 = get_png_path(toolkit, data, n, n_out, "reference", 1, ls, aa)
    reference_path_lw_same = get_png_path(toolkit, data, n, n_out, "reference", lw, ls, aa)

    dim = 1
    win_size = 11

    # read the images
    agg = (255 - 255 * plt.imread(agg_path)).astype(np.float32)
    ref_lw1 = ref_dict.get(str(reference_path_lw1), None)
    ref_same_lw = ref_dict.get(str(reference_path_lw_same), None)

    # fmt: off
    or_conv_same_lw = _get_or_conv_mask(agg[:, :, dim], ref_same_lw[:, :, dim], win_size)
    or_conv_lw_1 = _get_or_conv_mask(agg[:, :, dim], ref_lw1[:, :, dim], win_size)
    mse_list = (
        [
            _get_mse_series(agg, ref_same_lw, dim, or_conv_same_lw).add_suffix("_same_lw"),
            _get_mse_series(agg, ref_lw1, dim, or_conv_lw_1).add_suffix("_ref_lw=1"),
        ]
        if mse
        else []
    )

    ssim_dict_g = dict(ssim_kwargs)
    ssim_dict_g["gaussian_weights"] = True

    ssim_dict_no_g = dict(ssim_kwargs)
    ssim_dict_no_g["gaussian_weights"] = False

    # fmt: off
    return pd.concat(
        [
            pd.Series(
                index=["toolkit", "data", "aggregator", "n", "n_out", "ls", "lw", "aa"],
                data=[toolkit, data, aggregator, n, n_out, ls, lw, aa],
            ),
            _get_dssim_series(agg, ref_lw1, dim, or_conv_lw_1, **ssim_dict_no_g).add_suffix("_ref_lw=1"),
            _get_dssim_series(agg, ref_lw1, dim, or_conv_lw_1, **ssim_dict_g).add_suffix( "_guassian_ref_lw=1"),
            _get_dssim_series( agg, ref_same_lw, dim, or_conv_same_lw, **ssim_dict_no_g).add_suffix("_same_lw"),
            _get_dssim_series( agg, ref_same_lw, dim, or_conv_same_lw, **ssim_dict_g).add_suffix("_gaussian_same_lw"),
            *mse_list,
        ],
    )


def compute_dssim_matplotlib(
    agg_path: str | Path, ref_dict: dict, mse: bool, **ssim_kwargs
) -> pd.Series:
    """Compute the DSSIM, MSE, and MAE for a matplotlib figure.

    More specifically, this function computes the DSSIM for a reference figure with
    a line width of 1 and the same line width as the original figure.

    parameters
    ----------
    idx_r : pd.Series
        a row of the aggregation dataframe
    ref_dict : dict
        a dictionary of reference images, with the path as key and the image as value
    ssim_kwargs : dict
        keyword arguments for the skimage.metrics.structural_similarity function
    mse : bool
        whether to use the MSE as a metric as well

    returns
    -------
    pd.Series
        a row of the aggregation dataframe with the MSSIM and DSSIM values added
        More specifically, this function adds the following columns:
        - DSSIM_ref_lw=1
        - DSSIM_masked_ref_lw=1
        - DSSIM_same_lw
        - DSSIM_masked_same_lw
        - SSIM_ref_lw=1
        - SSIM_masked_ref_lw=1
        - SSIM_same_lw
        - SSIM_masked_same_lw

    """
    agg_path: Path = Path(agg_path)
    toolkit: str = agg_path.parent.name
    splits = (agg_path.name).split(".")[0].split("_")
    aggregator, data, n, n_out, ls, lw = splits[:6]
    # AA is an additional (last) name field for the matplotlib toolkit
    aa = len(splits) == 7
    ls = ls[3:]
    lw = lw[3:]

    # fmt: off
    reference_path_lw1 = get_png_path(toolkit, data, n, n_out, "reference", 1, ls, aa)
    reference_path_lw_same = get_png_path(
        toolkit, data, n, n_out, "reference", lw, ls, aa
    )

    dim = 3
    win_size = 11

    # read the images
    agg = 255 * plt.imread(str(agg_path)).astype(np.float32)
    ref_lw1 = ref_dict[str(reference_path_lw1)]
    ref_same_lw = ref_dict[str(reference_path_lw_same)]

    # fmt: off
    or_conv_same_lw = _get_or_conv_mask(agg[:, :, dim], ref_same_lw[:, :, dim], win_size)
    or_conv_lw_1 = _get_or_conv_mask(agg[:, :, dim], ref_lw1[:, :, dim], win_size)

    # fmt: off, None)]
    mse_list = (
        [
            _get_mse_series(agg, ref_same_lw, dim, or_conv_same_lw).add_suffix( "_same_lw"),
            _get_mse_series(agg, ref_lw1, dim, or_conv_lw_1).add_suffix("_ref_lw=1"),
        ]
        if mse
        else []
    )

    ssim_dict_g = dict(ssim_kwargs)
    ssim_dict_g["gaussian_weights"] = True

    ssim_dict_no_g = dict(ssim_kwargs)
    ssim_dict_no_g["gaussian_weights"] = False
    return pd.concat(
        [
            # fmt: off
            pd.Series(
                index=["toolkit", "data", "aggregator", "n", "n_out", "ls", "lw", "aa"],
                data=[toolkit, data, aggregator, n, n_out, ls, lw, aa],
            ),
            _get_dssim_series(agg, ref_lw1, dim, or_conv_lw_1, **ssim_dict_no_g).add_suffix( "_ref_lw=1"),
            _get_dssim_series(agg, ref_lw1, dim, or_conv_lw_1, **ssim_dict_g).add_suffix( "_guassian_ref_lw=1"),
            _get_dssim_series( agg, ref_same_lw, dim, or_conv_same_lw, **ssim_dict_no_g).add_suffix("_same_lw"),
            _get_dssim_series( agg, ref_same_lw, dim, or_conv_same_lw, **ssim_dict_g).add_suffix("_gaussian_same_lw"),
            *mse_list,
        ],
    )
