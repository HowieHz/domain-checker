import datetime

from dateutil import parser

from ..defined_types import Err, Ok, Result
from ..defined_types.datetime_parser_result import DatetimeParserErrResult


def datetime_string_parser(
    original_datetime: str,
) -> Result[datetime.datetime, DatetimeParserErrResult]:
    """
    将日期和时间的字符串表示解析为 datetime 对象。如果没有时区信息默认 utc

    Args:
        original_datetime (str): 要解析的日期和时间的字符串表示

    Returns:
        Result[datetime.datetime, DatetimeParserErrResult]: 表示解析后的日期和时间的 datetime 对象，时区为 utc
    """
    try:
        parsed_datatime: datetime.datetime = parser.parse(original_datetime.strip())

        # 没有时区信息默认 utc
        if parsed_datatime.tzinfo is None:
            return Ok(parsed_datatime.replace(tzinfo=datetime.timezone.utc))
        # 有则转换为 utc
        return Ok(parsed_datatime.astimezone(datetime.timezone.utc))
    except Exception as e:
        return Err({"msg": "Error Parsing Date", "err": e, "raw": original_datetime})
