import datetime
from typing import Literal

from ..date_utils import datetime_string_parser
from ..defined_types import Err, ParsedWhoisData, Result
from ..defined_types.datetime_parser_result import DatetimeParserErrResult


def whois_parser(raw_whois: str) -> ParsedWhoisData:
    """解析原始 whois 数据

    Args:
        raw_whois (str): 原始 whois 数据

    Returns:
        ParsedWhoisData: 解析后的结构化 whois 数据
    """
    return {
        "domain": "",
        "status": _check_domain_status(raw_whois),
        "raw": raw_whois,
        "registry_expiry_date": _whois_registry_expiry_date_parser(raw_whois),
    }


def _check_domain_status(
    raw_whois: str,
) -> tuple[bool, Literal["registered", "redemption", "unregistered"]]:
    """
    检查域名是否处于赎回期、已注册或未注册状态。

    Args:
        raw_whois (str): 原始 WHOIS 数据。

    Returns:
        Tuple[bool, str]: 返回一个元组，第一个元素表示是否为未注册状态，未注册则为 False。第二个元素表示状态（"registered", "redemption", "unregistered"）。
    """
    if "Domain Status: redemptionPeriod" in raw_whois:
        return (True, "redemption")
    elif any(
        keyword in raw_whois for keyword in ["Domain Name:", "domain:", "Domain name:"]
    ):
        return (True, "registered")
    else:
        return (False, "unregistered")


def _whois_registry_expiry_date_parser(
    raw_whois: str,
) -> Result[datetime.datetime, DatetimeParserErrResult]:
    # 一行一行遍历原始结果，找到包含指定开头的行
    for line in raw_whois.split("\n"):
        for prefix in [
            "Registrar Registration Expiration Date:",
            "Expiration Time:",
            "Registry Expiry Date:",
            "Expiry date:",
            "Expiry Date:",
        ]:
            if prefix in line:
                return datetime_string_parser(line.strip().removeprefix(prefix).strip())
    return Err(
        {"msg": "Date not found", "err": ValueError("Date not found"), "raw": raw_whois}
    )
