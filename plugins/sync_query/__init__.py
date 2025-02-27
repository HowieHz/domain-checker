import socket

from .whois_server_list import whois_server_dict

METADATA = {
    "id": "sync_query",
    "mode": "sync",
    "author": "HowieHz",
    "help": "调用内置 socket 库拉取 whois 信息",
}


def main(domain: str):
    try:
        if domain.endswith(".li") or domain.endswith(".ch"):
            # https://www.nic.li/whois/domaincheck/#collapse-c25cbf2f-a663-11e6-89db-525400a7a801-2
            raw_whois = whois_request(domain, "whois.nic.ch", port=4343)
            if raw_whois[1].startswith("1"):
                # Domain name can be registered
                return {"code": 200, "raw": raw_whois[1]}
            elif raw_whois[1].startswith("0"):
                # Domain name cannot be registered
                return {"code": 200, "raw": raw_whois[1]}
            elif raw_whois[1].startswith("-1"):
                # Invalid enquiry (i.e. modify enquiry prior to next attempt)
                return {"code": 503, "raw": raw_whois[1]}
            elif raw_whois[1].startswith("-95"):
                # Access restricted (i.e. wait a while and then try again)
                return {"code": 503, "raw": raw_whois[1]}
            elif raw_whois[1].startswith("-99"):
                # Temporary server error (i.e. wait a while and then try again)
                return {"code": 503, "raw": raw_whois[1]}

            return {"code": 503, "raw": raw_whois[1]}

        root_server = whois_server_dict[get_domain_tld(domain)]
        raw_whois = whois_request(domain, root_server)
        if raw_whois[0] == "Socket error":
            return {"code": 503, "raw": raw_whois[1]}
        # Your access is too fast,please try again later.\r\n
        if "Your access is too fast,please try again later." in raw_whois[1]:
            return {"code": 503, "raw": raw_whois[1]}
        if "Queried interval is too short." in raw_whois[1]:
            return {"code": 503, "raw": raw_whois[1]}
        return {"code": 200, "raw": raw_whois[1]}
    except Exception as e:
        return {"code": 500, "raw": e}


def get_domain_tld(domain: str) -> str:
    """
    解析出域名的顶级域名，并检查其是否在 whois_server_dict 的键中。

    Args:
        domain (str): 完整域名

    Returns:
        str: 顶级域名，如果不在字典中则返回空字符串
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
