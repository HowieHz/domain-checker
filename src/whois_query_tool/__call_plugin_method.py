from plugin_manager import PluginManager
from utils.defined_types import Err, Ok, ParsedWhoisData, PluginReturnDict, Result
from utils.defined_types.domain_query_result import ExceptionErrResult, MsgErrResult
from utils.whois_parser import whois_parser


def call_plugin_by_id(
    id: str, domain: str
) -> Result[ParsedWhoisData, MsgErrResult | ExceptionErrResult]:
    """调用指定 id 插件查询对应 domain 的 whois 数据

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

        return Ok({**whois_parser(ret["raw"]), "domain": domain})
    except Exception as e:
        # ExceptionErrResult
        return Err({"domain": domain, "err": e})
