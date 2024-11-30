import datetime

from .result import Ok, Err, Result

def is_expired(orginal_time: str) -> Result[bool, Exception]:
    """检查域名是否过期

    Args:
        time (str): whois 读取到的时间，如 2033-12-23T07:59:05Z

    Returns:
        Result[bool, Exception]: Ok(True) 为已过期，Ok(False) 为未过期，Err 为异常
    """
    try:
        if len(orginal_time) == 20:
            orginal_time_format = "%Y-%m-%dT%H:%M:%SZ"
        elif len(orginal_time) == 19:
            orginal_time_format = "%Y-%m-%d %H:%M:%S"
        else: 
            orginal_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        domain_expiration_timestamp = datetime.datetime.strptime(
            orginal_time, orginal_time_format
        ).timestamp()
        return Ok(
            domain_expiration_timestamp
            < datetime.datetime.now(datetime.timezone.utc).timestamp()
        )
    except Exception as e:
        return Err(e)
