"""
helper module for command line argument and initialization functions
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
import os
import argparse
import inspect
from pathlib import Path
import toml

from blast_defaults import SUCCESS, FAILURE
from blast_logging import log_exception, log_info

MODULE_NAME = Path(__file__).resolve().name
CWD_PATH = Path(__file__).resolve().parent


def parse_toml(config_path=Path(CWD_PATH, "config", "blast_cfg_example.toml"), logger=None) -> bool:
    """extracts values from '.toml' config file."""
    method = f"{inspect.currentframe().f_code.co_name}()"
    is_parsed = False
    try:
        if config_path.is_file() and config_path.stat().st_size > 0:
            config = toml.load(config_path)
            os.environ["ETL_NAME"] = config['etl']['name']
            os.environ["ETL_TIMEZONE"] = config["etl"]["timezone"]
            log_info(logger=logger, msg=f"{method} {SUCCESS} {config_path.name}")
            is_parsed = True
        else:
            raise FileNotFoundError
    except (KeyError, FileNotFoundError):
        log_exception(logger=logger, error_msg=f"{method} {FAILURE} {config_path.name}")
    return is_parsed


def parse_cmd_args(logger=None) -> dict:
    """ parse command line arguments"""
    method = f"{inspect.currentframe().f_code.co_name}()"
    valid_tbl = ["stg_data1", "stg_data2"]
    valid_db_env = ["development", "production"]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--days_ago",
        action="store",
        type=int,
        required=False,
        default=str(1),
        help="extract records starting with: n-days ago (default=5).",
    )
    parser.add_argument(
        "-db",
        "--db_environment",
        action="store",
        type=str,
        required=False,
        default="development",
        help=f"enter valid database environment: {valid_db_env}",
    )
    parser.add_argument(
        "-s",
        "--staging_table",
        action="store",
        type=str,
        required=False,
        default="stg_data1",
        help="enter specific staging table to process",
    )
    parser.add_argument(
        "-a",
        "--include_all",
        action="store",
        type=str,
        required=False,
        default="True",
        help="include_all=True: process all, if False: process single",
    )
    # convert parser to dict with vars()
    args = vars(parser.parse_args())

    days_ago = int(args["days_ago"])
    if days_ago < 0:
        print(f"{method} invalid: '{days_ago}' cannot be negative, using positive")
        days_ago *= -1
    args["days_ago"] = days_ago

    db_environment = args["db_environment"]
    if db_environment not in valid_db_env:
        parser.error(f"'{db_environment}' not in {valid_db_env}")

    staging_table = args["staging_table"]
    if staging_table not in valid_tbl:
        parser.error(f"'{staging_table}' not in {valid_tbl}")

    include_all = args["include_all"]
    if include_all.lower() in ["true", "t", "yes", "y", "1"]:
        args["include_all"] = True
    else:
        args["include_all"] = False
    log_info(logger=logger, msg=f"{method} {args}")
    return args


if __name__ == "__main__":
    parse_toml()
    parse_cmd_args()
