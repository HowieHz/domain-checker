from defined_types import Err, Ok, ParsedWhoisData, PluginReturnDict, Result
from defined_types.domain_query_result import ExceptionErrResult, MsgErrResult
from plugin_manager import PluginManager
from utils.whois_parser import whois_parser


def call_sync_plugin_by_id(
    id: str, domain: str
) -> Result[ParsedWhoisData, MsgErrResult | ExceptionErrResult]:
    """调用指定 id 插件查询对应 domain 的 whois 数据，插件为同步类型

    Args:
        id (str): 指定 id
        domain (str): 域名

    Returns:
        ParsedWhoisData: 解析后的 Whois 结构化数据
    """
    try:
        ret: PluginReturnDict = PluginManager().get_plugin_instance_by_id(id).main(domain)

        if ret["code"] != 200:
            # MsgErrResult
            return Err({"domain": domain, "msg": str(ret["raw"]), "code": ret["code"]})

        if ret["raw"] == "":
            return Err(
                {"domain": domain, "msg": "Empty query result", "code": ret["code"]}
            )

        # 预判常见的 API 错误返回，防止插件作者漏判，导致最终域名误判为未注册
        if any(
            msg in ret["raw"]
            for msg in [
                "Your access is too fast,please try again later.",
                "Queried interval is too short.",
            ]
        ):
            # MsgErrResult
            return Err({"domain": domain, "msg": str(ret["raw"]), "code": 503})

        return Ok({**whois_parser(ret["raw"]), "domain": domain})
    except Exception as e:
        # ExceptionErrResult
        return Err({"domain": domain, "err": e})


async def call_async_plugin_by_id(
    id: str, domain: str
) -> Result[ParsedWhoisData, MsgErrResult | ExceptionErrResult]:
    """调用指定 id 插件查询对应 domain 的 whois 数据，插件为异步类型

    Args:
        id (str): 指定 id
        domain (str): 域名

    Returns:
        ParsedWhoisData: 解析后的 Whois 结构化数据
    """
    try:
        ret: PluginReturnDict = (
            await PluginManager().get_plugin_instance_by_id(id).main(domain)
        )

        if ret["code"] != 200:
            # MsgErrResult
            return Err({"domain": domain, "msg": str(ret["raw"]), "code": ret["code"]})

        if ret["raw"] == "":
            return Err(
                {"domain": domain, "msg": "Empty query result", "code": ret["code"]}
            )

        return Ok({**whois_parser(ret["raw"]), "domain": domain})
    except Exception as e:
        # ExceptionErrResult
        return Err({"domain": domain, "err": e})
