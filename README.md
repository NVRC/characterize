

# characterize
Assess data across common dimensions.

## Usage
```bash
$ characterize --help
```

### Example
```bash
$ wget "https://huggingface.co/api/resolve-cache/datasets/AutonLab/Timeseries-PILE/ea89753da2b451928436adb333c7a2e892461c7d/forecasting%2Fautoformer%2Fweather.csv?download=true" -O /tmp/autonlab_timeseries_pile_weather.csv
$ characterize --path /tmp/autonlab_timeseries_pile_weather.csv
```
#### Primary plot
![Weather primary dataset example](./docs/img/example_weather.png)


## Data Model
```mermaid
flowchart LR

    Input[Data Input] --> Extension[Extension/MIME parsing]
    Extension --> Metadata[Extract metadata]
    Metadata --> Read[Read data]
    Read --> Features[Feature extraction]
    Metadata --> Features

    Features --> Qualitative

    Qualitative --> Type[Type/Class]
    Qualitative --> Category
    Type --> Scalar
    Type --> Vector
    Type --> Structured
    Type --> Time-series


    %% Quantitative dimensions
    Qualitative --> Quantitative
    Quantitative --> Quality
    Quantitative --> Profile

    Quality --> Accuracy
    Quality --> Coherence
    Quality --> Timeliness
    Quality --> Completeness

    %% Relative to other signals in the dataset
    Quality --> Consistency
    Quality --> Validity
    Quality --> Integrity

    Profile --> Distributions
    Profile --> Anomalies
    Profile --> Range[Range analysis]
    Profile --> Cardinality

```

### Signal/feature data quality
- _Accuracy_: degree to which data values reflect attributes of real-life entities.
- _Completeness_: extent of null attributes.
- _Timeliness_: newness of information.


### Classification
- _Precision_: measures correctness of _positive_ predictions.
- _Recall_: highlights how many _positives_ are captured within the dataset.
- _F1 Score_: balances precision and recall.

## Contributing
### Installation
We use [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) for dependency management and also recommend versioning Python with [PyEnv](https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv).

```bash
$ poetry install
$ poetry env activate
$ characterize --help
```
