import datetime
from typing import Literal, TypedDict

from ._result import Result
from .datetime_parser_result import DatetimeParserErrResult


class ParsedWhoisData(TypedDict, total=False):
    """whois 解析后的数据"""

    domain: str
    status: tuple[bool, Literal["registered", "redemption", "unregistered"]]
    raw: str
    registry_expiry_date: Result[datetime.datetime, DatetimeParserErrResult]
