<p align="center">
  <img src="https://repository-images.githubusercontent.com/685048321/921f44fe-e847-4eaa-8e6f-c04297e37949" width="350px" />
  <p align="center">A CLI to draw your data on top of millimeter paper</p>
</p>

*pappe* enables you to plot data (including error bars) on top of a given sheet of millimeter paper. It manages everything for you -- including the axis scaling. This way, you can use the tool's output as a template for your own diagram on millimeter paper.

Currently, pappe includes one type of millimeter paper in two orientations (portrait and landscape). However, you can also add your own millimeter paper (see advanced documentation).


## Run

You need to have [Python 3.11](https://www.python.org/downloads/) installed, so that the TOML parser is available.

Install the necessary python package used to annotate the PDF: `pip3 install pdf_annotate`

**Sample usage**

```
python3 pappe.py ./data/data.csv ./data/out.pdf
```

See the CLI help for more information. Alter the `config.toml` file to change the appearance.


## Basic documentation

To use pappe, specify the path to a CSV file holding the data as well as the desired output path for the PDF file.

```
python3 pappe.py <path to CSV> <PDF output path>
```

File paths are *relative* (see also `Sample usage` above).


<details>
<summary><b>CSV file</b></summary>

The supplied CSV file should have 2 to 4 columns and it must *not* have a header row. Each row represents one data point. This is what the columns are for:

| **Column 1** | **Column 2** | **Column 3**           | **Column 4** |
| ---          | ---          | ---                    | ---          |
| x-value      | y-value      | lower error of y-value* | upper error of y-value* |

\*Note: If only three columns are supplied, the third column's content is interpreted as a *symmetrical* error of the y-value.
</details>


<details>
<summary><b>Changing settings</b></summary>

To change basic settings, change the `config.toml` file. The following parameters can be set:

| Parameter | Type | Default | Meaning |
| --------- | ---- | ------- | ------- |
| `grid_variant` | `1` or `2` | `1` | `1` for portrait paper and `2` for landscape paper (you can also add your own paper; see advanced documentation). |
| `factors/x`, `factors/y` | `List<int>` | `[1, 2, 3, 4, 5, 6, 8, 9]` | The tool first tries to scale the data by the largest possible power of ten (so that your data still fits on the grid). It then chooses one of the supplied factors to further scale up the data; here again, it uses the largest possible factor. Change this array in order to obtain the desired scaling of the data in `x`- and `y`-direction. |
| `origins/x`, `origins/y` | `bool` | `false` | If you want the `x`- or `y`-axis to include the value `0`, set this to `true`. |
</details>


## Advanced documentation

As stated above, you can easily add your own millimeter paper by following the steps mentioned hereafter.

1. Add the pdf file of your millimeter paper to the `grids` folder.
2. Add an empty text file to the `grids` folder and name it `grid{n}.toml`. Populate this text file with the parameters mentioned below.

<details>
<summary><b>Grid config file</b></summary>

Adding your own millimeter paper requires you to 'measure' it. Read the following table chronologically for instructions:

| Parameter | Meaning / instructions |
| --- | --- |
| `paper/file` | Relative path of your grid pdf file (relative from the project's entry point). |
| `paper/width`, `paper/height` | Export your millimeter paper pdf file as a `jpg` image (e. g. with `300 ppi`). Input this image's pixel dimensions here. |
| `grid/width`, `grid/height` | Use a suitable image viewing application* to determine the pixel dimensions of the actual grid on your millimeter paper. |
| `grid/x`, `grid/y` | Use a suitable image viewing application* to determine the pixel position of the lower left corner of the actual grid on your millimeter paper. (This position should be measured from the lower left corner of your image.) |
| `grid/num_x_blocks`, `grid/num_y_blocks` | The number of *big* blocks on your millimeter paper. For example `18 x 27`. |
| `grid/num_x_tiny_blocks_per_block`, `grid/num_y_tiny_blocks_per_block` | Number of tiny blocks per big block. Usually, this number should be `10`. |
| `drawing/cross_size` | Pixel size of the displayed data points. |
| `drawing/axis_tick_size` | Pixel size of the axis ticks. |

\*For example preview on MacOS.
</details>