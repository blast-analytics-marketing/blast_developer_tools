"""
helper module for file utility functions
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
import inspect
import json
import string
import random
import hashlib
import uuid
import pprint as pp
from pathlib import Path
from blast_logging import log_exception, log_info, setup_logger
from blast_defaults import SUCCESS, ERROR, FAILURE

MODULE_NAME = Path(__file__).resolve().name
CWD_PATH = Path(__file__).resolve().parent

# ./blast_developer_tools/data/
DATA_PATH = Path(CWD_PATH.parent.parent, "data")
VALID_EXTENSIONS = [".csv", ".gzip", ".bz2", ".json"]


def print_data(title: str, data: object) -> None:
    """displays all data values to console as formatted string"""
    if data:
        print(f"\n{title}")
        pp.pprint(data, indent=2, width=180, compact=False, sort_dicts=False)


def touch_file(file_path: Path) -> bool:
    """exist_ok is true, FileExistsError exceptions will be ignored
    (same behavior as the POSIX mkdir -p command)"""
    is_created = False
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.is_file():
        # only touch if file does not exist
        file_path.touch(mode=0o777, exist_ok=True)
        is_created = True
    return is_created


def is_valid_file(file_path: Path) -> bool:
    """Checks if file: exists, is not directory, has correct extension and data"""
    is_valid = False
    if isinstance(file_path, Path) and file_path.is_file():
        if file_path.suffix in VALID_EXTENSIONS:
            if file_path.stat().st_size > 1:
                is_valid = True
    return is_valid


def get_file_size(file_path: Path) -> int:
    """Checks if file exists, is not directory, has correct extension, returns file_size in bytes"""
    file_size = 0
    if isinstance(file_path, Path) and file_path.is_file():
        if file_path.suffix in VALID_EXTENSIONS:
            file_size = file_path.stat().st_size
    return int(file_size)


def get_checksum(file_path: Path, enc_type: str = "sha3_224") -> dict:
    """returns hash of file contents, MD5/SHA1 have collisions
    SHA-2: sha224, sha256, sha384, sha512,
    SHA-3: sha3_224, sha3_256, sha3_512
    """
    checksum = {}
    if isinstance(file_path, Path) and file_path.is_file():
        # open as binary
        with open(str(file_path), "rb") as file_ptr:
            read_data = file_ptr.read()
            if enc_type == "sha224":
                sha_hash = hashlib.sha1(read_data)
            elif enc_type == "sha256":
                sha_hash = hashlib.sha256(read_data)
            elif enc_type == "sha512":
                sha_hash = hashlib.sha512(read_data)
            elif enc_type == "sha3_224":
                sha_hash = hashlib.sha3_224(read_data)
            else:
                # case: invalid input
                enc_type = "sha3_256"
                sha_hash = hashlib.sha3_256(read_data)
            file_ptr.close()
        checksum[enc_type] = str(sha_hash.hexdigest().upper())
    return checksum


def get_uuid_tag(trunc_len: int = 8) -> str:
    """generate globally unique UUID (truncated)"""
    return f"{str(uuid.uuid4())[:trunc_len]}"


def is_not_config(file_path: Path) -> bool:
    """return True if all items to avoid are not in file_path"""
    if isinstance(file_path, Path):
        avoid_items = [
            ".keep",
            "touch",
            ".lock",
            ".txt",
            ".DS_Store",
            "test_",
            ".toml",
            ".properties",
        ]
        for item in avoid_items:
            if item in str(file_path):
                return False
    return True


def get_directories_by_keyword(file_path: Path, keyword: str) -> list:
    """ non-recursive search for directory paths by keyword """
    method = f"{inspect.currentframe().f_code.co_name}()"
    dir_list = []
    if isinstance(file_path, Path):
        if file_path.exists():
            dir_list = [p.name for p in file_path.glob(f"*{keyword}*") if p.is_dir() and is_not_config(p)]
    else:
        print(f"{method} {ERROR} invalid type: {type(file_path)}")
    return sorted(dir_list)


def get_files_by_extension(file_path: Path, file_ext: str = ".csv") -> list:
    """ get non-recursive file paths by file extension """
    method = f"{inspect.currentframe().f_code.co_name}()"
    path_list = []
    if isinstance(file_path, Path):
        if file_path.exists():
            path_list = [p.absolute() for p in file_path.glob(f"*{file_ext}") if p.is_file() and is_not_config(p)]
    else:
        print(f"{method} {ERROR} invalid type: {type(file_path)}")
    return sorted(path_list)


def purge_prior_extract(file_path: Path, logger=None):
    """removes files from prior ETL processing"""
    method = f"{inspect.currentframe().f_code.co_name}()"
    try:
        all_paths = []
        purged_files = []
        for file_ext in [".csv", ".gzip", ".bz2", ".json"]:
            all_paths.extend(get_files_by_extension(file_path, file_ext))
        for remove_path in all_paths:
            os.remove(remove_path)
            purged_files.append(remove_path.name)
        purge_count = len(all_paths)
        if purge_count > 0:
            log_info(logger=logger, msg=f"{method} removed {purge_count} file(s) {purged_files}")
    except (OSError, PermissionError):
        log_exception(logger=logger, error_msg=f"{method} {FAILURE} {file_path}")


def join_sub_folder(cwd_path=DATA_PATH, folders=["subdir1", "subdir2"], filename: str = "nested.txt") -> Path:
    """join subfolders to Path object, create directories and touch file as needed
    input:
        folders = ["subdir1", "subdir2"] (as list)
        folders = "subdir1,subdir2" (as comma delimited string)
    """
    subdir_list = []
    if isinstance(folders, list):
        subdir_list.extend(folders)
    if isinstance(folders, str):
        subdir = folders.replace(" ", "")
        if "," in folders:
            subdir_list = subdir.split(",")
        else:
            subdir_list = [folders]
    subdir_list.append(filename)
    child_path = cwd_path.joinpath(*subdir_list)
    if not child_path.parent.exists():
        child_path.parent.mkdir(parents=True, exist_ok=True)
    touch_file(child_path)
    return child_path


def read_json(file_path: Path, logger=None) -> dict:
    """ open and read source '.json' file """
    method = f"{inspect.currentframe().f_code.co_name}()"
    try:
        if file_path.is_file():
            with open(file_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
                json_file.close()
                if not json_data:
                    log_info(logger=logger, msg=f"{method} EMPTY: {file_path.name}")
                return json_data
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        log_exception(logger=logger, error_msg=f"{method} {FAILURE} '{file_path.name}'")
    return None


def write_json(output_path: Path, data: dict, logger=None) -> None:
    """ exports request data to '.json' formatted file. """
    method = f"{inspect.currentframe().f_code.co_name}()"
    try:
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        if data:
            with open(output_path, "w", encoding="utf-8") as json_file:
                formatted_str = json.dumps(data, indent=2, sort_keys=False)
                json_file.write(formatted_str)
                json_file.close()
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        log_exception(logger=logger, error_msg=f"{method} {FAILURE} '{output_path}'")


def write_txt(output_path: Path, data: str, logger=None) -> None:
    """ exports string to '.txt' file """
    method = f"{inspect.currentframe().f_code.co_name}()"
    if isinstance(output_path, Path) and data:
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(output_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(str(data))
                txt_file.close()
                log_info(logger=logger, msg=f"{method} {SUCCESS} {output_path.name}")
        except (OSError, ValueError):
            log_exception(logger=logger, error_msg=f"{method} {ERROR} {output_path.name}")
    else:
        print(f"{method} {ERROR} invalid input: {type(output_path)}")


def generate_random_data(file_path, binary=False, megabytes=0.01, logger=None) -> bool:
    """
    generate binary file with the specified size in bytes
    :param file_path:  data source to file path
    :param binary: if random binary data should be generated
    :param mega_bytes: file size in megabytes (1024 base)
    :return: bool if created
    """
    method = f"{inspect.currentframe().f_code.co_name}()"
    is_generated = False
    # convert megabytes to bytes
    file_size_bytes = int(megabytes * 1024 * 1024)
    try:
        if binary:
            file_path = Path(file_path.parent, f"{file_path.name}")
            with open(file_path, "wb") as fp:
                fp.write(os.urandom(int(file_size_bytes)))
        else:
            file_path = Path(file_path.parent, f"{file_path.name}")
            with open(file_path, "w") as fp:
                letters = []
                letters.extend(string.ascii_letters)
                letters.extend(string.punctuation)
                letters.extend(string.digits)
                random.shuffle(letters)
                diff_size = file_size_bytes
                while diff_size > 0:
                    random_str = "".join([random.choice(letters) for c in range(1, len(letters))])
                    if len(random_str) <= diff_size:
                        bytes_written = fp.write(random_str)
                    else:
                        bytes_written = fp.write(random_str[:diff_size])
                    diff_size -= bytes_written

        stat_size = file_path.stat().st_size
        if file_path.is_file() and stat_size >= file_size_bytes:
            log_info(logger=logger, msg=f"{file_path.name} ({stat_size} bytes)")
            is_generated = True
    except AttributeError:
        log_exception(logger=logger, error_msg=f"{method} {file_path.name}")
    except FileNotFoundError:
        log_exception(logger=logger, error_msg=f"{method} {file_path.name}")
    return is_generated


if __name__ == "__main__":
    LOGGER = setup_logger(MODULE_NAME)
    print(f"CWD_PATH: {CWD_PATH}")
    print(f"DATA_PATH: {DATA_PATH}")
    generate_random_data(file_path=DATA_PATH.joinpath(*["binary_data.txt"]), binary=True, logger=LOGGER)
    generate_random_data(file_path=join_sub_folder(filename="nested_data.txt"), binary=False, logger=LOGGER)
