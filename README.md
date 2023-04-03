# Representativity of time series data aggregation algorithms

<!-- <div align="center">
<h1>
    <p>Data Point Selection for Line Chart Visualization:</p>
    <p>Methodological Assessment and Evidence-Based Guidelines</p>
</h1>
</div> -->


Codebase & further details for the paper: 
> **Data Point Selection for Line Chart Visualization: Methodological Assessment and Evidence-Based Guidelines**  
> Jonas Van Der Donckt, Jeroen Van Der Donckt

Preprint: :construction:

## How is the repository structured?

- The codebase is located in the `agg_utils` folder.
- Additional details can be found in the respective README.md files in the `details` folder.
- Supplementary gifs can be found in the `gifs` folder.
- See [notebooks README](notebooks/) for the more details.
  - The `0.*` notebooks are used for data parsing and figure generation.
  - The `1.*` notebooks are used for the analysis (visual representativeness and visual stability).
  - The `varia_*` notebooks are used to illustrate OR-conv, toolkit comparison, and M4 pixel-perfect nuances.

Folder structure
```txt
├── agg_utils          <- shared codebase for the notebooks
├── details            <- additional details in README.md files
├── gifs               <- supplementary gifs
├── loc_data           <- local data folder 
└─── notebooks          <- main notebooks see README.md
```

## [notebooks README](notebooks/)

Folder structure
```txt
├── agg_utils          <- shared codebase for the notebooks
├── loc_data           <- local data folder 
└─── notebooks          <- main notebooks see README.md
    └── playground      <- playground notebooks see README.md
```

## How to install the requirements?

This repository uses [poetry](https://python-poetry.org/) as dependency manager.  
A specification of the dependencies is provided in the [`pyproject.toml`](pyproject.toml) and [`poetry.lock`](poetry.lock) files.

You can install the dependencies in your Python environment by executing the following steps;
1. Install poetry: https://python-poetry.org/docs/#installation
2. Activate you poetry environment by calling `poetry shell`
3. Install the dependencies by calling `poetry install`

## Utilizing this repository

Make sure that you've extended the [path_conf.py](agg_utils/path_conf.py) file's hostname if statement with your machine's hostname and that you've configured the path to the UCR archive folder.


---

<p align="center">
👤 <i>Jonas & Jeroen Van Der Donckt</i>
</p>
