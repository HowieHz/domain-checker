import datetime

from defined_types import Err, Ok, Result


def is_datetime_expired(target_datetime: datetime.datetime) -> Result[bool, Exception]:
    """检查某个 datetime 对象表示的时间是否比现在早

    Args:
        target_datetime (datetime.datetime): 原始 datetime 对象，如无时区信息，默认为 utc

    Returns:
        Result[bool, Exception]: Ok(True) 为已过期（传入时间比现在早），Ok(False) 为未过期（传入时间比现在晚），Err(Exception) 表示出现异常
    """
    try:
        # 检查时区信息
        if target_datetime.tzinfo != datetime.timezone.utc:
            if target_datetime.tzinfo is None:
                target_datetime = target_datetime.replace(tzinfo=datetime.timezone.utc)
            else:
                # 将 target_datetime 转换为 UTC
                target_datetime = target_datetime.astimezone(datetime.timezone.utc)

        # 获取当前时间
        current_datetime = datetime.datetime.now(datetime.timezone.utc)

        is_expired = target_datetime < current_datetime

        return Ok(is_expired)
    except Exception as e:
        return Err(e)
