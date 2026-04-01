"""Categorize a MIME type to a Dataset descriptor."""

from enum import StrEnum
from typing import Callable, Dict, NamedTuple

import pandas as pd


class DatasetCategory(StrEnum):
    TIMESERIES = "TIMESERIES"
    SEMI_STRUCTURED = "SEMI_STRUCTURED"


DatasetPointer = NamedTuple(
    "DatasetPointer", [("category", DatasetCategory), ("parser", Callable[[str], pd.DataFrame])]
)


class MIMECategorizer:
    """Translate MIME to a dataset category.
    Supported MIME registries are a subset of:
        - text/
        - application/
    """

    SUPPORTED_REGISTRIES = ("text", "application")

    MIME_DATASET_CATEGORY: Dict[str, DatasetPointer] = {
        "application/vnd.apache.parquet": DatasetPointer(DatasetCategory.TIMESERIES, pd.read_parquet),
        "text/csv": DatasetPointer(DatasetCategory.TIMESERIES, pd.read_csv),
        "application/json": DatasetPointer(DatasetCategory.SEMI_STRUCTURED, pd.read_json),
    }

    @staticmethod
    def categorize(mime: str) -> DatasetPointer:
        # Apply str regex to roughly map MIME types to common fmts
        # with the end goal of parsing the data.
        # e.g. `text/csv` implies Tabular data and other assumptions/views
        #       may then be futher applied.
        if not mime.startswith(MIMECategorizer.SUPPORTED_REGISTRIES):
            raise NotImplementedError(
                "Must be of format {}. Cannot categorize mime {}.".format(MIMECategorizer.SUPPORTED_REGISTRIES, mime)
            )
        dataset_type = MIMECategorizer.MIME_DATASET_CATEGORY.get(mime, None)
        if dataset_type is None:
            raise NotImplementedError("MIME {} not supported.".format(mime))
        return dataset_type
