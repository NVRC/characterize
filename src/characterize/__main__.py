import argparse
import logging
import mimetypes
import sys
from pathlib import Path

from characterize.descriptor import describe
from characterize.mime import MIMECategorizer


CLI_LOCAL_PATH = "path"


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
        # Coerce DataFrame dtypes
        df = df.convert_dtypes(
            infer_objects=True,
            convert_string=True,
            convert_integer=True,
            convert_boolean=True,
            convert_floating=True,
            dtype_backend="numpy_nullable",
        )

        descriptive_df = df.describe()

        logging.debug("Sample DataFrame: \n%s", df)
        logging.debug("DataFrame Dtypes: \n%s", df.dtypes)
        logging.debug("Descriptive DataFrame: \n%s", descriptive_df)
        # Extract semantic metadata from column names
        data_descriptor = describe(Path(url), column_names=list(df.columns))
        logging.info("Data descriptor: %s", data_descriptor)

        # Feature extraction and view assessment

    except Exception as ex:
        logging.critical(str(ex))
        return 1
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
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
    args = parser.parse_args()
    sys.exit(main(args.path))
