from typing import Any, Literal, TypedDict


class PluginMetadataDict(TypedDict, total=False):
    """插件元数据数据类型"""

    id: str
    mode: Literal["sync", "async"]  # 标记是同步型还是异步型
    author: tuple[str] | str
    help: str
    # option: str
    # version: str
    # tag: list[str]


class PluginReturnDict(TypedDict):
    """插件返回值数据类型"""

    code: int
    raw: Any
