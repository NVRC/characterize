import argparse
import logging
import mimetypes
import sys
from pathlib import Path
from typing import Optional

from characterize.data import descriptor
from characterize.data.plots import render
from characterize.mime import MIMECategorizer


CLI_LOCAL_PATH = "path"
CLI_PRIMARY_INDEX = "index"

LOG_FMT = (
    "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
)


def main(path: Path, index_col: Optional[str]) -> int:
    try:
        # Parse extension
        # The canonical MIME formats:
        #   https://www.iana.org/assignments/media-types/media-types.xhtml
        mime_type, _ = mimetypes.guess_type(path, strict=False)
        logging.info("Parsed mime %s from dataset path %s", mime_type, path)
        if mime_type is None:
            raise ValueError("Unable to parse mime type from url {}".format(path))

        dataset_type = MIMECategorizer.categorize(mime_type)
        logging.info("Determined dataset category %s", dataset_type.category)

        # Read Data
        df = dataset_type.parser(path)
        # Coerce DataFrame dtypes
        df = df.convert_dtypes(
            infer_objects=True,
            convert_string=True,
            convert_integer=True,
            convert_boolean=True,
            convert_floating=True,
            dtype_backend="numpy_nullable",
        )
        if index_col:
            df = df.set_index(keys=index_col, drop=True)

        descriptive_df = df.describe()

        logging.debug("Sample DataFrame: \n%s", df)
        logging.debug("DataFrame Dtypes: \n%s", df.dtypes)
        logging.debug("Descriptive DataFrame: \n%s", descriptive_df)
        # Extract semantic metadata from column names
        data_descriptor = descriptor.describe(path, column_names=list(df.columns))
        logging.info("Data descriptor: %s", data_descriptor)

        # Feature extraction and view assessment
        # Derive a shared index
        render(data_descriptor, df)

    except Exception as ex:
        logging.critical(str(ex))
        return 1
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FMT,
    )
    mimetypes.init()
    parser = argparse.ArgumentParser("Characterize a dataset.")
    parser.add_argument(
        "-p",
        f"--{CLI_LOCAL_PATH}",
        help="Local path to a homogenous set of data.",
        dest=CLI_LOCAL_PATH,
        type=str,
        required=True,
    )
    parser.add_argument(
        "-i",
        f"--{CLI_PRIMARY_INDEX}",
        help="Primary dataset index, UTC timestamp recommended.",
        dest=CLI_PRIMARY_INDEX,
        type=str,
        required=False,
    )
    args = parser.parse_args()
    sys.exit(main(Path(args.path), args.index))
