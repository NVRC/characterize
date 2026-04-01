import argparse
import logging
import mimetypes
import sys
from enum import StrEnum
from typing import Callable, Dict, NamedTuple

import pandas as pd


CLI_DATA_URL = "url"


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


def main(url: str) -> int:
    try:
        # Parse extension
        # The canonical MIME list is https://www.iana.org/assignments/media-types/media-types.xhtml
        mime_type, _ = mimetypes.guess_type(url, strict=False)
        logging.info("Parsed mime %s from dataset url %s", mime_type, url)
        if mime_type is None:
            raise ValueError("Unable to parse mime type from url {}".format(url))

        dataset_type = MIMECategorizer.categorize(mime_type)
        logging.info("Determined dataset category %s", dataset_type.category)

        # Read Data
        df = dataset_type.parser(url)
        descriptive_df = df.describe()

        logging.info("Sample DataFrame: %s", df)
        logging.info("Descriptive DataFrame: %s", descriptive_df)
        # Extract semantic metadata from columns

        # Feature extraction and view assessment

    except Exception as ex:
        logging.critical(str(ex))
        return 1
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
    )
    mimetypes.init()
    parser = argparse.ArgumentParser("Characterize a dataset.")
    parser.add_argument(
        "-i",
        f"--{CLI_DATA_URL}",
        help="URL to a homogenous set of data.",
        dest=CLI_DATA_URL,
        type=str,
        required=True,
    )
    args = parser.parse_args()
    sys.exit(main(args.url))
