"""
helper module for datetime functions
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
from pathlib import Path
from datetime import datetime, timedelta
import pytz

MODULE_NAME = Path(__file__).resolve().name
CWD_PATH = Path(__file__).resolve().parent


def get_time_zone(timezone="America/Los_Angeles"):
    """
    return validated time zone
    """
    valid_tz = "America/Los_Angeles"
    if timezone in pytz.common_timezones:
        valid_tz = timezone
    return pytz.timezone(valid_tz)


def get_start_end_dates(days_ago: int = 14) -> tuple:
    """returns strings for two dates since today (based on timezone)"""
    curr_end_date = datetime.now(tz=get_time_zone())
    past_start_date = curr_end_date - timedelta(days=days_ago)
    return past_start_date.strftime("%Y-%m-%d"), curr_end_date.strftime("%Y-%m-%d")


def parse_date_str(date="2022-01-01", date_fmt="%Y-%m-%d") -> datetime:
    """attempt to convert date with specific date format
       strptime: convert string to datetime object
       strftime: convert datetime object back to string
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior"""
    date_dt = None
    try:
        date_dt = datetime.strptime(date, date_fmt)
    except ValueError:
        print(f"INVALID_DATE: '{date}' format: {date_fmt}")
    return date_dt


def calculate_days_since(date: str = "2022-01-01") -> int:
    """returns number of days between now() and date string"""
    days_ago = 0
    curr_date = datetime.now()
    hist_date = parse_date_str(date=date, date_fmt="%Y-%m-%d")
    if isinstance(hist_date, datetime):
        days_ago = (curr_date - hist_date).days
    return int(days_ago)


def get_historical_date(days: int = 5) -> str:
    """returns strings for two dates (based on timezone)"""
    curr_date = datetime.now(tz=get_time_zone())
    hist_date = curr_date - timedelta(days=days)
    return hist_date.strftime("%Y-%m-%d")


def get_date_today() -> str:
    """Generates timestamp string from now() used to tag resources format: YYYY-MM-DD"""
    date_today = datetime.now(tz=get_time_zone()).strftime("%Y-%m-%d")
    return f"{date_today}"


def get_etl_pull_date() -> str:
    """
    Generates timestamp string from now() used to tag resources
    format: YYYY-MM-DD HH:MM:SS (no AM/PM or timezone)
    """
    etl_pull_date = datetime.now(tz=get_time_zone()).strftime("%Y-%m-%d %H:%M:%S")
    return f"{etl_pull_date}"


def get_timestamp(path_version=False) -> str:
    """
    Generates timestamp string from now() used to tag resources with AM/PM and timezone
    format: YYYY-MM-DD HH:MM:SS AM/PM PST/EST
    """
    time_now = datetime.now(tz=get_time_zone()).strftime("%Y-%m-%d %H:%M:%S %p %Z")
    if path_version:
        # if file path: replace colon with hyphen and space with underscore
        time_now = time_now.replace(":", "-").replace(" ", "_")
    return f"{time_now}"


if __name__ == "__main__":
    print(f"MODULE_NAME: {MODULE_NAME}")
    print(f"CWD_PATH: {CWD_PATH}")
    print(get_timestamp())
    print(get_historical_date(days=3))
    print(calculate_days_since())
    print(get_start_end_dates())
