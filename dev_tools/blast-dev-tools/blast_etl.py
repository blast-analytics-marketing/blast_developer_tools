"""
helper module for ETL functions
"""
# Copyright 2021, Blast Analytics & Marketing
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import inspect
from pathlib import Path
from datetime import datetime
import pandas as pd
from blast_logging import log_exception, log_info, setup_logger
from blast_defaults import SUCCESS, FAILURE, WARNING, ERROR
import blast_etl_dtypes as dtypes

MODULE_NAME = Path(__file__).resolve().name
CWD_PATH = Path(__file__).resolve().parent


def get_staging_tables(subfolder="subfolder1") -> list:
    """include_all=False: use single staging table provided from command line args"""
    method = f"{inspect.currentframe().f_code.co_name}()"
    staging_tables = []
    valid_directories = list(dtypes.DW_TABLE_MAP.keys())
    if subfolder in valid_directories:
        staging_tables = dtypes.DW_TABLE_MAP[subfolder].get("staging_tables", [])
    else:
        print(f"{method} {ERROR} {subfolder} not in {valid_directories}")
    return staging_tables


def set_difference(src_A: list, dst_B: list) -> list:
    """returns set difference of src_A and dst_B
    A\\B or A-B = {x: x ∈ A and x ∉ B} a.k.a LEFT OUTER JOIN
    only values in src_A that are NOT in dst_B are returned"""
    diff_list = []
    if isinstance(src_A, list) and isinstance(dst_B, list):
        diff_list = sorted(list(set(src_A) - set(dst_B)))
    return diff_list


def print_dtypes(title: str, ds: pd.Series, show_numbers: bool = True) -> None:
    """ displays dataframe dtypes (pd.Series) to console output """
    method = f"{inspect.currentframe().f_code.co_name}()"
    if isinstance(ds, pd.Series):
        count = 0
        print(f"\n{method} {title}")
        for key, val in ds.iteritems():
            if show_numbers:
                print(f"\t{str(val):16}\t{key:48}\tcol_{count:02}")
            else:
                print(f"\t{str(val):16}\t{key:48}")
            count += 1
    else:
        print(f"{method} {FAILURE} invalid type {type(ds)}")


def std_dtypes(sf_object: str, df: pd.DataFrame, logger=None) -> pd.DataFrame:
    """convert data types in pandas as needed"""
    method = f"{inspect.currentframe().f_code.co_name}()"
    pd_float_64 = pd.Float64Dtype()
    pd_int_64 = pd.Int64Dtype()
    try:
        col_list = df.columns.values.tolist()
        for col_name in col_list:
            if col_name in dtypes.ALL_STRING_COLUMNS:
                continue
            if col_name in dtypes.ALL_FLOAT_COLUMNS:
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce", downcast=None)
                df[col_name] = df[col_name].astype(dtype=pd_float_64, errors="ignore")
            elif col_name in dtypes.ALL_BOOL_COLUMNS:
                df[col_name] = df[col_name].map({True: "true", False: "false"})
            elif col_name in dtypes.ALL_TIMESTAMP_COLUMNS:
                df[col_name] = pd.to_datetime(df[col_name], errors="coerce")
                df[col_name] = df[col_name].dt.strftime("%Y-%m-%d %H:%M:%S")
            elif col_name in dtypes.ALL_DATE_COLUMNS:
                df[col_name] = pd.to_datetime(df[col_name], errors="coerce")
                df[col_name] = df[col_name].dt.strftime("%Y-%m-%d")
            elif col_name in dtypes.ALL_INT_COLUMNS:
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce", downcast=None)
                df[col_name] = df[col_name].astype(dtype=pd_int_64, errors="ignore")
        # df.drop_duplicates(keep="last", inplace=True)
        pull_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df["etl_pull_date"] = pull_date
        log_info(logger=logger, msg=f"{method} {SUCCESS} pull_date: '{pull_date}'")
        return df
    except (OSError, PermissionError, ValueError, pd.errors.DtypeWarning):
        log_exception(logger=logger, error_msg=f"{method} {FAILURE} '{sf_object}'")
        return pd.DataFrame()


def read_csv_to_df(file_path: Path, logger=None) -> pd.DataFrame:
    """ import source '.csv' file to pandas dataframe """
    try:
        if isinstance(file_path, Path) and file_path.is_file():
            if file_path.suffix in [".csv", ".gzip", ".bz2"]:
                df = pd.read_csv(
                    file_path,
                    sep=",",
                    engine="c",
                    encoding="utf-8",
                    na_filter=False,
                    keep_default_na=True,
                    dtype=object,
                    low_memory=False,
                )
                if isinstance(df, pd.DataFrame):
                    return df
    except (AttributeError, ValueError, pd.errors.DtypeWarning):
        log_exception(logger=logger, error_msg=f"'{file_path}'")
    return pd.DataFrame()


def write_df_to_csv(output_path: Path, df: pd.DataFrame, compression=None, header=True, logger=None) -> None:
    """ exports dataframe to comma-delimited, fully-quoted '.csv' file (where csv.QUOTE_ALL = 1)"""
    method = f"{inspect.currentframe().f_code.co_name}()"
    if compression not in ["gzip", "bz2"]:
        compression = None
    if isinstance(output_path, Path) and isinstance(df, pd.DataFrame):
        try:
            row_count = df.shape[0]
            if row_count > 0:
                if not output_path.parent.exists():
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(
                    output_path,
                    sep=",",
                    date_format="%Y-%m-%d",
                    encoding="utf-8",
                    quoting=1,
                    quotechar='"',
                    compression=compression,
                    index=False,
                    header=header,
                )
                if output_path.is_file():
                    log_info(logger=logger, msg=f"{method} {SUCCESS} '{output_path.name}' ({row_count} ROWS)")
            else:
                log_info(logger=logger, msg=f"{method} {WARNING} dataframe empty (no rows) '{output_path.name}'")
        except (OSError, ValueError, pd.errors.DtypeWarning):
            log_exception(logger=logger, error_msg=f"{method} {FAILURE} '{output_path}'")
    else:
        log_info(logger=logger, msg=f"{method} {FAILURE} invalid types: {type(output_path)} {type(df)}")


if __name__ == "__main__":
    LOGGER = setup_logger(MODULE_NAME)
    print(f"CWD_PATH: {CWD_PATH}")
    dtypes.show_data("staging_tables", data=get_staging_tables())
