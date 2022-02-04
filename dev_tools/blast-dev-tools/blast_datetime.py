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
from datetime import datetime, timedelta, timezone
import pytz

MODULE_NAME = Path(__file__).resolve().name
CWD_PATH = Path(__file__).resolve().parent


def get_time_zone(tzinfo="America/Los_Angeles"):
    """
    return validated time zone
    """
    valid_tz = "UTC"
    if tzinfo in pytz.common_timezones:
        valid_tz = tzinfo
    return pytz.timezone(valid_tz)


def get_start_end_dates(days_ago: int = 14) -> tuple:
    """returns strings for two dates since today (based on timezone)"""
    curr_end_date = datetime.now(tz=get_time_zone())
    past_start_date = curr_end_date - timedelta(days=days_ago)
    return past_start_date.strftime("%Y-%m-%d"), curr_end_date.strftime("%Y-%m-%d")


def parse_date_str(date_str="2022-01-01", date_fmt="%Y-%m-%d") -> datetime:
    """attempt to convert date with specific date format
       strptime: convert string to datetime object
       strftime: convert datetime object back to string
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior"""
    date_obj = None
    try:
        date_obj = datetime.strptime(date_str, date_fmt)
    except ValueError:
        print(f"INVALID_DATE: '{date_str}' format: {date_fmt}")
    return date_obj


def calculate_days_since(date_str="2022-01-01") -> int:
    """returns number of days between now() and date string"""
    days_ago = 0
    curr_date = datetime.now()
    hist_date = parse_date_str(date_str=date_str, date_fmt="%Y-%m-%d")
    if isinstance(hist_date, datetime):
        days_ago = (curr_date - hist_date).days
    return int(days_ago)


def get_historical_date(days_ago: int = 5) -> str:
    """returns strings for two dates (based on timezone)"""
    curr_date = datetime.now(tz=get_time_zone())
    hist_date = curr_date - timedelta(days=days_ago)
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


def get_start_current_month() -> datetime:
    """Generates timestamp from now() for first day (midnight) of current calendar month:"""
    start_current_month_dt = datetime.now(tz=get_time_zone()).replace(microsecond=0)
    return start_current_month_dt.replace(day=1, hour=0, minute=0, second=0)


def get_end_current_month() -> datetime:
    """Generates timestamp string from now() for last day of current calendar month:"""
    date_today_dt = datetime.now(tz=get_time_zone()).replace(microsecond=0)
    next_month_dt = date_today_dt.replace(day=28) + timedelta(days=4)
    end_of_month_dt = next_month_dt - timedelta(days=next_month_dt.day)
    return end_of_month_dt.replace(hour=23, minute=59, second=59)


def get_end_last_month() -> datetime:
    """Generates timestamp from now() for last day at 23:59:59 of current calendar month:"""
    return get_start_current_month() - timedelta(seconds=1)


def is_start_of_month() -> bool:
    """
    Checks if timestamp from now() is after first day at midnight of current calendar month
    """
    method = f"{inspect.currentframe().f_code.co_name}()"
    is_first = False
    timestamp_now_dt = datetime.now(tz=get_time_zone()).replace(microsecond=0)
    start_current_month_dt = get_start_current_month()
    diff_ts = timestamp_now_dt - start_current_month_dt
    if timestamp_now_dt.day == start_current_month_dt.day:
        is_first = True
    return is_first


def get_date_range(start_date="2022-01-01", end_date="2022-01-07", date_fmt="%Y-%m-%d", tzinfo=timezone.utc) -> list:
    """returns list of timezone aware datetime objects"""
    date_range = []
    start_date = parse_date_str(date_str=start_date, date_fmt=date_fmt)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tzinfo)

    end_date = parse_date_str(date_str=end_date, date_fmt=date_fmt)
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tzinfo)

    next_date = start_date
    while next_date <= end_date:
        date_range.append(next_date)
        next_date += timedelta(days=1)
    return date_range


if __name__ == "__main__":
    print(f"MODULE_NAME: {MODULE_NAME}")
    print(f"CWD_PATH: {CWD_PATH}")
    print(get_timestamp())
    print(get_historical_date(days_ago=3))
    print(calculate_days_since())
    print(get_start_end_dates())
    print(calculate_days_since(date_str="2021-12-01"))
    print(get_start_current_month())
    print(get_end_current_month())
    print(get_date_range())
