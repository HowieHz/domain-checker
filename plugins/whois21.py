from whois21 import WHOIS

from src.utils.defined_types import PluginMetadataDict, PluginReturnDict

METADATA: PluginMetadataDict = {
    "id": "whois21",
    "mode": "sync",
    "author": "HowieHz",
    "help": "调用 whois21 库拉取 whois 信息",
}


def main(domain: str) -> PluginReturnDict:
    # 返回值 200 还非空，就会进入检查
    # 返回值 200 但是 raw 为空，会设置为 Empty query result
    # 返回值非 200 不论 raw 是什么都会按照 API Error 输出
    # 所以如果返回值为 200 且 raw 非空，但不是正常的 whois 内容，就随便填一个非 200 的 code，如下面的 503，避免误判为 Not Register
    try:
        raw_whois = WHOIS(domain=domain, timeout=10).raw.decode("utf-8")
        # Your access is too fast,please try again later.\r\n
        if "Your access is too fast,please try again later." in raw_whois:
            return {"code": 503, "raw": raw_whois}
        return {"code": 200, "raw": raw_whois}
    except Exception as e:
        return {"code": 500, "raw": e}
