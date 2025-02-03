import sys
from pathlib import Path

# 用于加载插件目录下（如 plugins/whois21/）的附加库文件
sys.path.append(str(Path(__file__).resolve().parent))

from whois21 import WHOIS

METADATA = {
    "id": "whois21",
    "mode": "sync",
    "author": "HowieHz",
    "help": "调用 whois21 库拉取 whois 信息",
}


def main(domain: str):
    try:
        raw_whois = WHOIS(domain=domain, timeout=10).raw.decode("utf-8")
        # Your access is too fast,please try again later.\r\n
        if "Your access is too fast,please try again later." in raw_whois:
            return {"code": 503, "raw": raw_whois}
        return {"code": 200, "raw": raw_whois}
    except Exception as e:
        return {"code": 500, "raw": e}
