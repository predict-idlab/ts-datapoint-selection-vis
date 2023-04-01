from typing import Literal, Optional, Tuple

import matplotlib.lines as lines

"""Wittholds code for constructing figures with matplotlib and plotly."""

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from bokeh.io import export_png
from bokeh.models import Range1d
from bokeh.plotting import figure


def return_matplotlib_arr(
    x,
    y,
    dpi=96,
    width=800,
    height=250,
    aa: bool = True,
    line_width_px: int = 1,
    drawstyle: Literal[
        "default", "steps", "steps-pre", "steps-mid", "steps-post"
    ] = "default",
    xlim: Optional[Tuple] = None,
    ylim: Optional[Tuple] = None,
) -> np.ndarray:
    """Construct a matplotlib figure and return it as a numpy array.

    parameters
    ----------
    x : array-like
        x data
    y : array-like
        y data
    save_path : str
        path to save the figure to
    dpi : int
        dpi of the figure
    width : int
        width of the figure in pixels
    height : int
        height of the figure in pixels
    aa : bool
        whether to use anti-aliasing or not, defaults to True
    line_width_px : int
        width of the line in pixels
    drawstyle : str
        drawstyle of the line; must be one of the following:
        'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'
    xlim : tuple
        x limits of the figure
    ylim : tuple
        y limits of the figure

    .. Note::
        If you want to ensure that the images are 1-to-1 comparable you should always
        set the xlim and ylim to the same values for all images.

    """
    line_width_points = line_width_px / dpi * 72
    fig = plt.figure(frameon=False, dpi=dpi, linewidth=line_width_points)
    fig.set_size_inches(width / dpi, height / dpi)

    # make an ax that is the size of the figure
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    ax.add_line(
        lines.Line2D(
            xdata=x,
            ydata=y,
            c="black",
            aa=aa,
            linewidth=line_width_points,
            drawstyle=drawstyle,
        )
    )
    # Scale x and y to the data ranges
    ax.set_xlim((x[0], x[-1]) if xlim is None else xlim)
    ax.set_ylim((min(y), max(y)) if ylim is None else ylim)

    # Add the line to the axes
    fig.add_axes(ax, projection=None)
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    return arr


def construct_matplotlib_fig(
    x,
    y,
    save_path,
    dpi=96,
    width=800,
    height=250,
    aa=True,
    line_width_px=1,
    xlim: Optional[Tuple] = None,
    ylim: Optional[Tuple] = None,
    drawstyle: Literal[
        "default", "steps", "steps-pre", "steps-mid", "steps-post"
    ] = "default",
    return_fig=False,
    backend="agg",
):
    """Construct a matplotlib figure and save it to a file.

    parameters
    ----------
    x : array-like
        x data
    y : array-like
        y data
    save_path : str
        path to save the figure to
    dpi : int
        dpi of the figure
    width : int
        width of the figure in pixels
    height : int
        height of the figure in pixels
    aa : bool
        whether to use anti-aliasing or not, defaults to True
    line_width_px : int
        width of the line in pixels
    xlim : tuple
        x limits of the figure
    ylim : tuple
        y limits of the figure
    drawstyle : str
        drawstyle of the line; must be one of the following:
        'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'
    return_fig : bool
        whether to return the figure or not, defaults to False

    """
    line_width_points = line_width_px / dpi * 72
    fig = plt.figure(frameon=False, dpi=dpi, linewidth=line_width_points)
    fig.set_size_inches(width / dpi, height / dpi)
    # make an ax that is the size of the figure
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    # Scale x and y to the data ranges
    ax.add_line(
        lines.Line2D(
            xdata=x,
            ydata=y,
            c="black",
            aa=aa,
            linewidth=line_width_points,
            drawstyle=drawstyle,
        )
    )

    ax.set_xlim((x[0], x[-1]) if xlim is None else xlim)
    ax.set_ylim((min(y), max(y)) if ylim is None else ylim)

    # Add the line to the axes
    fig.add_axes(ax, projection=None)
    fig.savefig(
        save_path,
        dpi=dpi,
        # bbox_inches="tight",
        pad_inches=0,
        backend=backend,
    )
    if return_fig:
        return fig
    plt.close(fig)
    del fig, ax


def construct_plotly_fig(
    x,
    y,
    save_path,
    width=800,
    height=250,
    aa=True,
    line_width=1,
    line_shape: Literal["linear", "spline", "hv", "vhv", "hvh"] = "linear",
    xlim=None,
    ylim=None,
):
    """Construct a plotly figure and save it to a file.

    parameters
    ----------
    x : array-like
        x data
    y : array-like
        y data
    save_path : str
        path to save the figure to
    width : int
        width of the figure in pixels
    height : int
        height of the figure in pixels
    line_shape : str
        shape of the line; must be one of the following:
        'linear', 'spline', 'hv', 'vh', 'hvh', 'vhv'
    line_width : int
        width of the line in pixels
    aa : bool
        whether to use anti-aliasing can only be True!
    xlim : tuple
        x limits of the figure
    ylim : tuple
        y limits of the figure

    """
    assert aa, "Plotly does not support setting anti-aliasing to False."

    fig = go.Figure()
    axis_kwargs = dict(
        showgrid=False, zeroline=False, automargin=False, showticklabels=False
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0, pad=0),
        width=width,
        height=height,
        template=None,
        xaxis=axis_kwargs,
        yaxis=axis_kwargs,
    )
    fig.add_trace(
        go.Scatter(
            name="ball",
            line=dict(shape=line_shape, color="black", width=line_width),
            x=x,
            y=y,
        )
    )
    if xlim is not None:
        fig.update_xaxes(range=xlim)
    if ylim is not None:
        fig.update_yaxes(range=ylim)

    with open(save_path, "wb") as f:
        f.write(fig.to_image(format="png", width=width, height=height))


def construct_bokeh_fig(
    x,
    y,
    save_path,
    width=800,
    height=250,
    aa=True,
    line_width=1,
    line_shape: Literal["default", "steps-mid"] = "default",
    xlim=None,
    ylim=None,
):
    """Construct a bokeh figure and save it to a file.

    parameters
    ----------
    x : array-like
        x data
    y : array-like
        y data
    save_path : str
        path to save the figure to
    width : int
        width of the figure in pixels
    height : int
        height of the figure in pixels
    aa : bool
        whether to use anti-aliasing can only be True!
    line_shape : str
        shape of the line; must be one of the following:
        'default', 'steps-mid'
    line_width : int
        width of the line in pixels
    xlim : tuple
        x limits of the figure
    ylim : tuple
        y limits of the figure

    """
    assert aa, "Bokeh does not support setting anti-aliasing to False."
    p = figure(width=width, height=height)
    if line_shape == "default":
        p.line(x, y, line_width=line_width, line_color="black")
    elif line_shape == "steps-mid":
        p.step(x, y, line_width=line_width, mode="center", line_color="black")
    else:
        raise ValueError(f"Invalid line-shape: {line_shape}")
    p.axis.visible = False
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.min_border_left = 0
    p.min_border_right = 0
    p.min_border_top = 0
    p.min_border_bottom = 0
    if xlim is not None:
        p.x_range = Range1d(xlim[0], xlim[-1])
    p.y_range = Range1d(ylim[0], ylim[-1])
    p.background_fill_color = None
    p.border_fill_color = None
    p.toolbar_location = None
    p.margin = 0
    p.min_border = 0
    p.outline_line_color = None

    export_png(p, filename=save_path)
