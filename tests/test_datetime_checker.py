import datetime

from src.defined_types import Err, Ok
from src.utils.date_utils import is_datetime_expired


# 过去的日期：确保函数返回 Ok(True)
def test_is_datetime_expired_past():
    past_datetime = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
    result = is_datetime_expired(past_datetime)
    assert isinstance(result, Ok)
    assert result.value == True


# 未来的日期：确保函数返回 Ok(False)
def test_is_datetime_expired_future():
    future_datetime = datetime.datetime(3000, 1, 1, tzinfo=datetime.timezone.utc)
    result = is_datetime_expired(future_datetime)
    assert isinstance(result, Ok)
    assert result.value == False


# 没有时区信息的日期：默认使用 UTC 进行比较
def test_is_datetime_expired_no_timezone():
    past_datetime = datetime.datetime(2000, 1, 1)
    result = is_datetime_expired(past_datetime)
    assert isinstance(result, Ok)
    assert result.value == True


# 不同时区的日期：将日期转换为 UTC 后进行比较
def test_is_datetime_expired_different_timezone():
    past_datetime = datetime.datetime(
        2000, 1, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=-5))
    )
    result = is_datetime_expired(past_datetime)
    assert isinstance(result, Ok)
    assert result.value == True


# 无效输入：传递非 datetime 对象应返回 Err(AttributeError)
def test_is_datetime_expired_invalid_input():
    result = is_datetime_expired("invalid_datetime")
    assert isinstance(result, Err)
    assert isinstance(result.error, AttributeError)
