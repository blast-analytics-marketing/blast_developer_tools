"""
helper module for logging and environment functions
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
import sys
import inspect
import logging
from pathlib import Path
import platform
import json
from datetime import datetime
import pprint as pp
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import pkg_resources

MODULE_PATH = Path(__file__).resolve()
# ./blast_developer_tools/logs/
CWD_PATH = MODULE_PATH.parent.parent


def setup_logger(
        src_file: Path,
        log_file=Path(CWD_PATH.parent, "logs", "blast_dev_tools.log"), std_out: bool = True
) -> logging.Logger:
    """logging setup with both file and console output"""
    if not log_file.parent.exists():
        log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(str(src_file))
    logger.setLevel(logging.INFO)
    log_format = "%(asctime)s [%(levelname)s] pid:%(process)d | %(filename)s:%(lineno)d | %(message)s"
    formatter = logging.Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S.%M %Z")
    # create a file handler
    file_handler = logging.FileHandler(str(log_file))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # also print STDOUT to console for debugging
    if std_out:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)
    return logger


def log_info(logger=None, msg: str = None) -> None:
    """print message to console if logger=None"""
    logger.info(msg) if logger else print(msg)


def log_exception(logger=None, error_msg: str = None) -> None:
    """ custom exception handling logging function."""
    ex_type, ex_value, ex_tb = sys.exc_info()
    ex_type = f"{ex_type}" if ex_type else ""
    ex_value = " ".join(f"{str(ex_value)}".split()) if ex_value else ""
    src_name = f"{os.path.split(ex_tb.tb_frame.f_code.co_filename)[1]}" if ex_tb else ""
    line_num = f"{ex_tb.tb_lineno}" if ex_tb else ""
    base_msg = f"{ex_type} {ex_value} | {src_name}:{line_num}"
    exc_msg = f"{error_msg} | {base_msg}" if error_msg else base_msg
    logger.error(exc_msg) if logger else print(exc_msg)


def get_isp_sys_info() -> dict:
    """Get current ISP and system information of connected host."""
    isp_req = Request("http://ipinfo.io/json")
    isp_data = {"isp_info": {"hostname": "localhost"}}
    try:
        isp_data["isp_info"].update(json.load(urlopen(isp_req)))
    except HTTPError as ex:
        isp_data["status"] = f"HTTPError code: {ex.code} {ex.reason}"
    except URLError as ex:
        isp_data["status"] = f"URLError: {ex.reason}"
    isp_data["isp_info"]["arch"] = f"{platform.system()} {platform.architecture()[0]} " f"{platform.machine()}"
    isp_data["isp_info"]["time"] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    if "readme" in isp_data["isp_info"]:
        del isp_data["isp_info"]["readme"]
    pp.pprint(isp_data, indent=2, width=72, compact=False, sort_dicts=False)
    return isp_data


def is_running_in_production(prod_hostname_tag="PROD") -> bool:
    """True: if running on production compute instance with 'PROD' substring in hostname"""
    curr_hostname = str(platform.node())
    # case in-sensitive string compare
    return prod_hostname_tag.lower() in curr_hostname.lower()


def is_running_in_development() -> bool:
    """used to set debug value to True, if running locally"""
    return not is_running_in_production()


def get_hostname() -> str:
    """hostname of system"""
    return str(platform.node()).lower().replace(".local", "")


def get_current_username() -> str:
    """Returns current username on host."""
    try:
        curr_username = os.getlogin()
    except OSError:
        curr_username = "docker"
    return curr_username


def get_relevant_env_vars(include_all=False) -> dict:
    """shows environmental variables"""
    env_dict = {}
    if include_all:
        env_dict.update(dict(os.environ))
        env_dict.pop("PATH")
        env_dict.pop("PYTHONPATH")
    else:
        env_vars = [
            "ETL_NAME",
            "ETL_TIMEZONE",
        ]
        for env_name, val in os.environ.items():
            if env_name in env_vars:
                env_dict[env_name] = val
    if env_dict:
        print(f"host: '{platform.node()}'")
        pp.pprint(env_dict, indent=2, width=64, compact=False, sort_dicts=False)
    return env_dict


def set_env_variable(key="PY_ENVIRONMENT", val="production") -> None:
    """Set environmental variables: DEV, STG, PROD"""
    method = f"{inspect.currentframe().f_code.co_name}()"
    # for value to string
    os.environ[key] = str(val)
    result = False
    if isinstance(val, bool):
        result = bool(os.environ.get(key).lower() in ["true", "t", "yes", "y", "1"])
    elif isinstance(val, str):
        result = os.environ.get(key)
    if result != val:
        print(f"{method} {result} != {val}")


def check_platform() -> str:
    """checks host operating system running python module."""
    sys_platform = sys.platform
    host_os = "unknown"
    if "linux" in sys_platform:
        print(f"{platform.node()} running on Linux")
        host_os = "linux"
    elif "darwin" in sys_platform:
        print(f"{platform.node()} running on MacOS")
        host_os = "macos"
    elif "win" in sys_platform:
        print(f"{platform.node()} running on Windows")
        host_os = "win"
    return host_os


def show_installed_packages() -> None:
    """Returns currently installed python packages on host."""
    working_set = list(pkg_resources.working_set)
    # case insensitive sorting
    installed_pkgs = sorted(
        [f"{pkg.project_name:}=={pkg.version}" for pkg in working_set],
        key=lambda s: s.lower(),
    )
    for i, pkg in enumerate(installed_pkgs, start=1):
        print(f"\tpkg_{i:02}\t {pkg}")


if __name__ == "__main__":
    get_isp_sys_info()
    show_installed_packages()
