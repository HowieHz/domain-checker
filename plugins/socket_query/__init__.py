import socket

from src.utils.defined_types import PluginMetadataDict, PluginReturnDict

from .whois_server_list import whois_server_dict

METADATA: PluginMetadataDict = {
    "id": "socket_query",
    "mode": "sync",
    "author": "HowieHz",
    "help": "调用内置 socket 库拉取 whois 信息",
}


# 传入域名的根域名要求 xn--
def main(domain: str) -> PluginReturnDict:
    # 返回值 200 还非空，就会进入检查
    # 返回值 200 但是 raw 为空，会设置为 Empty query result
    # 返回值非 200 不论 raw 是什么都会按照 API Error 输出
    # 所以如果返回值为 200 且 raw 非空，但不是正常的 whois 内容，就随便填一个非 200 的 code，如下面的 503，避免误判为 Not Register
    try:
        root_server = whois_server_dict[get_root_domain(domain)]
        raw_whois = whois_request(domain, root_server)
        if raw_whois[0] == "Socket error":
            return {"code": 503, "raw": raw_whois[1]}
        # Your access is too fast,please try again later.\r\n
        if "Your access is too fast,please try again later." in raw_whois[1]:
            return {"code": 503, "raw": raw_whois[1]}
        return {"code": 200, "raw": raw_whois[1]}
    except Exception as e:
        return {"code": 500, "raw": e}


def get_root_domain(domain: str) -> str:
    """
    解析出域名的根域名，并检查其是否在 whois_server_dict 的键中。

    Args:
        domain (str): 完整域名

    Returns:
        str: 根域名，如果不在字典中则返回空字符串
    """
    domain_parts = domain.lower().split(".")
    for i in range(len(domain_parts)):
        potential_root = ".".join(domain_parts[i:])
        if potential_root in whois_server_dict:
            return potential_root
    return ""


def whois_request(domain: str, server: str, port=43, timeout=15) -> tuple:
    try:
        with socket.create_connection((server, port), timeout) as sock:
            sock.sendall(("%s\r\n" % domain).encode("utf-8"))
            response = bytearray()
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                response.extend(data)
        return (200, response.decode("utf-8"))
    except socket.error as e:
        return ("Socket error", e)
