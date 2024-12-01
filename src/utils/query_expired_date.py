import asyncio
from whois21 import WHOIS

from .result import Ok, Err, Result
from .logger import debug


async def whois_query(domain: str) -> Result[dict, dict]:
    """通过 whois 查询域名信息

    Args:
        domain (str): 主域名.顶级域名 的形式

    Returns:
        Result[dict, dict]: 查询结果
    """
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, WHOIS, domain)

        status = result.get("DOMAIN STATUS")
        if type(status) is not list:
            status = [status]

        domain_name = result.get("DOMAIN NAME")
        if domain_name is None:
            register = False
        else:
            register = True

        answer = {
            "code": 200,
            "domain": str(domain_name).lower(),
            "iana": result.get("REGISTRAR IANA ID"),
            "whois-ser": result.get("REGISTRAR WHOIS SERVER"),
            "ser-url": result.get("REGISTRAR URL"),
            "updated_date": result.get("UPDATED DATE"),
            "creation_date": result.get("CREATION DATE"),
            "expired_date": result.get("REGISTRY EXPIRY DATE"),
            "ser-name": result.get("REGISTRAR"),
            "status": status,
            "dns": result.get("NAME SERVER"),
            "dnssec": result.get("DNSSEC"),
            "update_db_date": result.get("LAST UPDATE OF WHOIS DATABASE"),
            "raw": result.raw.decode("utf-8"),
            "register": register,
        }
        return Ok(answer)
    except Exception as e:
        return Err({"code": 500, "msg": e})


async def query_expired_date(domain: str) -> Result[str, str]:
    """通过 whois 查询域名过期时间

    Args:
        domain (str): 主域名.顶级域名 的形式

    Returns:
        Result[str, str]: 过期时间，可能的形式为 2033-12-23T07:59:05Z 或 2033-12-23T07:59:05.000Z
    """
    query_ret = await whois_query(domain)

    match query_ret:
        case Ok(value):
            result = value
        case Err(_error):
            return Err("Not Found")
    
    if result["code"] != 200:
        return Err(f"Internat Error {result['code']}")
    
    if result["expired_date"] is not None:
        return Ok(result["expired_date"])
    # 一行一行遍历 raw 结果，找到包含 'Expiration Time' 的行
    for line in result["raw"].split("\n"):
        if "Expiration Time" in line:
            return Ok(line.removeprefix("Expiration Time: ").strip())
        if "Registry Expiry Date" in line:
            return Ok(line.removeprefix("Registry Expiry Date: ").strip())
    if result["register"] == False:
        return Err("Not Register")  # 未注册
    debug(f"{domain} 未找到过期时间", result)
    return Err("Not Found Date")


if __name__ == "__main__":

    async def main():
        result = await query_expired_date("luogu.com.cn")
        match result:
            case Ok(value):
                print(value)
            case Err(error):
                print(error)

    asyncio.run(main())
