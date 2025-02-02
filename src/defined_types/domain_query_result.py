from typing import TypedDict


class MsgErrResult(TypedDict):
    domain: str
    msg: str
    code: int


class ExceptionErrResult(TypedDict):
    domain: str
    err: Exception
