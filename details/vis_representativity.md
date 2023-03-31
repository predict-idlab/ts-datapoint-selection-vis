# Visual Representativity

This markdown file accompanies the interactive visualization of the `Visual Representativity` sectio of the paper with some insights and explanations.

`TODO`: 
- add a table of contents
- describe some terms (data efficiency, the Metrics, add the formula of the elbow)


### Image template grid & toolkit

All visualizations utilize a line-width of 2 and linear interpolation.

![](../gifs/toolkit_aa.gif)

**insights**:
- the order of the trends is preserved among the different toolkits
- aliasing causes the `PEM_20` to drop significanly
    - the anti-aliased figures seem to staturate at a `PEM_20` of .0.1, which is caused by the shading differences between the anti-aliasedaggregation and reference images
- `LTTB` and `MinMax` seems to perform the best `TODO`
- There seems to be some instability in the M4 metrics for the `Ball-200k` template. 
    Analysis shows that is caused by the granularity of M4, slightly mismapping the reference image to the aggregated image. The screenshot below demonstrates that a lower n-out had a better mapping of this double peak at the end than a higher n_out (which utilized a lot of pixel space, hence it weighs a lot in the visual representativity metrics)
    ![](_figs/instability_n_out_ball_200k.png)


### Image template gride & line width

The employed toolkit is Plotly, using its default configurations i.e. a line width of 2 
and a linear interpolation. The metrics are computed using refrence images of the same line width.

![](../gifs/plotly_default_slider%3Dlw.gif)

**insights**:
- Increasing the line-width causes the metrics to decrease
- we observe some **inconsistencies** in the trend for the `plotly` and `bokeh` toolkit for lw=1. Specifically, for the `DSSIM` and `PEM_20` metrics. These inconsistencies are caused by the aggregation back-end for these toolkits and consecutive datapoint pixel column changes. Specifically the `DSSIM` error can be attributed to the aggregation backend interleaving small gaps for the reference error. 
    - The visualization below demonstrates how the matplotlib ref (middle subplot first row) does  not contain any empty areas, whereas the plotly reference visualization (muddle subplot second row) does contain empty areas, explaining hte high `DSSIM` error.
    ![](_figs/plotly_matplotib_lttb_lw%3D1.png)  <!-- N = 50k -->
    - The visualization below demonstrates how the `PEM_20` metric is affected by the datapoint pixel column mapping. We observe that fewer empty spaces are noticeable for the Plotly aggregation with n_out=1600 (left subplot first row) than for the aggregation (left subplot second row) with n_out=2320. This is caused by slight changes in datapoint to pixel-column mapping. Given that LTTB favors bin-centered datapoints, an `n_out` that is not a multitude of the canvas width will thus cause that the detapoints are not located in the same x-position of surrounding pixel-columns, resulting in more empty spaces (until n_out increases more so that the empty spaces will be again filled in)
    ![](_figs/plotly_lw%3D1_pem_pixel_column_mapping.png)  <!-- N = 50k -->
