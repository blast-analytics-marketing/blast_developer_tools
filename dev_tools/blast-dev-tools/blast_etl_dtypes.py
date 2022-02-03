"""
helper module for data type defaults
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
import pprint as pp


def show_data(title: str, data: object) -> None:
    """displays all data values to console as formatted string"""
    if data:
        print(f"\n{title}")
        pp.pprint(data, indent=2, width=180, compact=False, sort_dicts=False)


DW_TABLE_MAP = {
    "subfolder1": {
        "staging_tables": [
            "01_stg_table",
            "02_stg_table",
            "03_stg_table",
            "04_stg_table",
        ]
    },
    "subfolder2": {
        "staging_tables": [
            "01_stg_table",
            "02_stg_table",
            "03_stg_table",
            "04_stg_table",
            "05_stg_table",
            "06_stg_table",
        ]
    },
}

OBJECT_MAP = {
    "ObjectName1": {
        "field1_str": "object",
        "field2_str": "object",
        "field3_bool": "bool",
        "field4_date": "date64",
        "field5_timestamp": "datetime64",
        "field6_int": "int64",
        "field7_float": "float64",
        "field8_int": "int64",
        "field9_date": "date64",
    },
    "ObjectName2": {
        "field1_timestamp": "datetime64",
        "field2_str": "object",
        "field3_bool": "bool",
        "field4_date": "date64",
        "field5_float": "float64",
        "field6_int": "int64",
        "field7_bool": "bool",
        "field8_timestamp": "datetime64",
        "field9_int": "int64",
    },
}

ALL_STRING_COLUMNS = []
ALL_INT_COLUMNS = []
ALL_FLOAT_COLUMNS = []
ALL_BOOL_COLUMNS = []
ALL_DATE_COLUMNS = []
ALL_TIMESTAMP_COLUMNS = []
ALL_COLUMNS = []

for obj_name, field_lut in OBJECT_MAP.items():
    for field, pd_type in field_lut.items():
        if "object" in pd_type and field not in ALL_STRING_COLUMNS:
            ALL_STRING_COLUMNS.append(field)
        elif "int64" in pd_type and field not in ALL_INT_COLUMNS:
            ALL_INT_COLUMNS.append(field)
        elif "float64" in pd_type and field not in ALL_FLOAT_COLUMNS:
            ALL_FLOAT_COLUMNS.append(field)
        elif "bool" in pd_type and field not in ALL_BOOL_COLUMNS:
            ALL_BOOL_COLUMNS.append(field)
        elif "date64" in pd_type and field not in ALL_DATE_COLUMNS:
            ALL_DATE_COLUMNS.append(field)
        elif "datetime64" in pd_type and field not in ALL_TIMESTAMP_COLUMNS:
            ALL_TIMESTAMP_COLUMNS.append(field)
        if field not in ALL_COLUMNS:
            ALL_COLUMNS.append(field)

PD_TYPE_MAP = {
    "object": ALL_STRING_COLUMNS,
    "int64": ALL_INT_COLUMNS,
    "float64": ALL_FLOAT_COLUMNS,
    "bool": ALL_BOOL_COLUMNS,
    "date64": ALL_DATE_COLUMNS,
    "datetime64": ALL_TIMESTAMP_COLUMNS,
}


def show_datatype_frequency():
    """optimization: check frequency of datatypes"""
    total_fields = 0
    for field_dict in list(OBJECT_MAP.values()):
        total_fields += len(field_dict)
    print(f"\nALL_STRING_COLUMNS    \tcount: {len(ALL_STRING_COLUMNS)} \t{ALL_STRING_COLUMNS}")
    print(f"ALL_INT_COLUMNS       \tcount: {len(ALL_INT_COLUMNS)} \t{ALL_INT_COLUMNS}")
    print(f"ALL_FLOAT_COLUMNS     \tcount: {len(ALL_FLOAT_COLUMNS)} \t{ALL_FLOAT_COLUMNS}")
    print(f"ALL_BOOL_COLUMNS      \tcount: {len(ALL_BOOL_COLUMNS)} \t{ALL_BOOL_COLUMNS}")
    print(f"ALL_DATE_COLUMNS      \tcount: {len(ALL_DATE_COLUMNS)} \t{ALL_DATE_COLUMNS}")
    print(f"ALL_TIMESTAMP_COLUMNS \tcount: {len(ALL_TIMESTAMP_COLUMNS)} \t{ALL_TIMESTAMP_COLUMNS}")
    print(f"ALL_COLUMNS           \tcount: {len(ALL_COLUMNS)} \t{ALL_COLUMNS}")
    print(f"TOTAL_FIELDS          \tcount: {total_fields}")


if __name__ == "__main__":
    show_data(title="PD_TYPE_MAP", data=PD_TYPE_MAP)
    show_data(title="OBJECT_MAP", data=OBJECT_MAP)
    show_datatype_frequency()
    show_data(title="DW_TABLE_MAP", data=DW_TABLE_MAP)
