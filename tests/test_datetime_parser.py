import datetime

import pytest

from src.utils.date_utils import datetime_string_parser


# 有效的日期字符串测试
@pytest.mark.parametrize(
    "date_string, year, month, day, hour, minute, second",
    [
        ("2033-12-23T07:59:05Z", 2033, 12, 23, 7, 59, 5),
        ("2028-09-13T07:00:00+0000", 2028, 9, 13, 7, 0, 0),
        ("2025-01-01T00:00:00.0Z", 2025, 1, 1, 0, 0, 0),
        ("2010-05-20T15:45:30+0530", 2010, 5, 20, 10, 15, 30),
        ("1999-12-31T23:59:59-0800", 2000, 1, 1, 7, 59, 59),
        ("2025-01-01 00:00:00", 2025, 1, 1, 0, 0, 0),
        ("2025-11-09 22:31:20+00:00", 2025, 11, 9, 22, 31, 20),
        ("12-Feb-2026", 2026, 2, 12, 0, 0, 0),
    ],
)
def test_datetime_string_parser_valid(
    date_string, year, month, day, hour, minute, second
):
    result = datetime_string_parser(date_string)
    assert result.value.year == year
    assert result.value.month == month
    assert result.value.day == day
    assert result.value.hour == hour
    assert result.value.minute == minute
    assert result.value.second == second
    assert result.value.tzinfo == datetime.timezone.utc


# 无效的日期字符串测试
@pytest.mark.parametrize(
    "raw",
    [
        "Invalid Date String",
        "2028-09-13T07!00:00+0000",
        "2025-S",
        "2010-05-99",
        "1999-12-31T23:59:99-0800",
        "2025-88-09 22:31:20+00:00",
    ],
)
def test_datetime_string_parser_invalid(raw):
    result = datetime_string_parser(raw)
    assert result.error["msg"] == "Error Parsing Date"
    assert result.error["raw"] == raw
    assert isinstance(result.error["err"], Exception)


# 边界测试：闰年日期
def test_datetime_string_parser_leap_year():
    leap_date = "2020-02-29T12:00:00Z"
    result = datetime_string_parser(leap_date)
    assert result.value.year == 2020
    assert result.value.month == 2
    assert result.value.day == 29
    assert result.value.hour == 12
    assert result.value.minute == 0
    assert result.value.second == 0
    assert result.value.tzinfo == datetime.timezone.utc


# 边界测试：最早可表示的日期
def test_datetime_string_parser_earliest_date():
    earliest_date = "0001-01-01T00:00:00Z"
    result = datetime_string_parser(earliest_date)
    assert result.value.year == 1
    assert result.value.month == 1
    assert result.value.day == 1
    assert result.value.hour == 0
    assert result.value.minute == 0
    assert result.value.second == 0
    assert result.value.tzinfo == datetime.timezone.utc


# 测试不同的时间格式
@pytest.mark.parametrize(
    "date_string, year, month, day, hour, minute, second",
    [
        ("March 15, 2021, 13:45:00", 2021, 3, 15, 13, 45, 0),
        ("2021/03/15 13:45:00", 2021, 3, 15, 13, 45, 0),
        ("15-03-2021 13:45:00", 2021, 3, 15, 13, 45, 0),
        ("2021.03.15 13:45:00", 2021, 3, 15, 13, 45, 0),
    ],
)
def test_datetime_string_parser_various_formats(
    date_string, year, month, day, hour, minute, second
):
    result = datetime_string_parser(date_string)
    assert result.value.year == year
    assert result.value.month == month
    assert result.value.day == day
    assert result.value.hour == hour
    assert result.value.minute == minute
    assert result.value.second == second


# 测试时区偏移
def test_datetime_string_parser_timezone_offset():
    date_string = "2021-03-15T13:45:00-0500"
    result = datetime_string_parser(date_string)
    assert result.value.year == 2021
    assert result.value.month == 3
    assert result.value.day == 15
    assert result.value.hour == 18  # 13:45 -05:00 转换为 UTC 是 18:45
    assert result.value.minute == 45
    assert result.value.second == 0
    assert result.value.tzinfo == datetime.timezone.utc
