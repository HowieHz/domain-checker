from typing import TypedDict


class DatetimeParserErrResult(TypedDict):
    err: Exception
    msg: str
    raw: str
