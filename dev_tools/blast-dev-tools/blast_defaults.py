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
"""
default values for modules
"""
DEBUG = False
STATUS = {True: "SUCCESS", False: "ERROR"}

SUCCESS = "SUCCESS:"
ERROR = "ERROR:"
FAILURE = "FAILURE:"
WARNING = "WARNING:"

TIMEZONES = {
    "eastern": {"zone": "America/New_York", "abbr": "EST", "utc": "UTC-5"},
    "central": {"zone": "America/Chicago", "abbr": "CST", "utc": "UTC-6"},
    "mountain": {"zone": "America/Denver", "abbr": "MST", "utc": "UTC-7"},
    "pacific": {"zone": "America/Los_Angeles", "abbr": "PST", "utc": "UTC-8"},
    "anywhere": {"zone": "Pacific/Baker_Island", "abbr": "AoE", "utc": "UTC-12"},
    "utc": {"zone": "UTC", "abbr": "UTC", "utc": "UTC-0"},
}
