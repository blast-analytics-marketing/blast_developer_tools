"""
main driver module
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
import time
from pathlib import Path
from blast_datetime import get_timestamp
from blast_files import generate_random_data
from blast_logging import setup_logger
from blast_init_cmd_args import parse_cmd_args, parse_toml, get_relevant_env_vars

MODULE_NAME = Path(__file__).resolve().name
CWD_PATH = Path(__file__).resolve().parent

# ./blast_developer_tools/data/
DATA_PATH = Path(CWD_PATH, "data")

LOGGER = setup_logger(MODULE_NAME)

if __name__ == "__main__":
    print(f"{MODULE_NAME} started: {get_timestamp()}")
    start = time.perf_counter()

    parse_cmd_args(logger=LOGGER)
    parse_toml(logger=LOGGER)
    get_relevant_env_vars()

    generate_random_data(
        file_path=DATA_PATH.joinpath(*["ascii_data.txt"]),
        binary=False, megabytes=0.02, logger=LOGGER,
    )

    print(f"{MODULE_NAME} finished: {time.perf_counter() - start:0.2f} seconds")
