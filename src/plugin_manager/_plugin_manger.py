import importlib
import os
import sys
import traceback
from types import ModuleType
from typing import Any, Generator

from src.defined_types import PluginMetadataDict
from src.utils.text import PLUGIN_DIR_LOAD_ERROR, PLUGIN_FILE_LOAD_ERROR

# 为了导入上层包
sys.path.append(os.path.join(sys.path[0], ".."))

from pathlib import Path
from typing import Any, Generator


def _get_single_file_plugins(
    plugin_dir: Path, plugin_file_suffix: str
) -> Generator[str, Any, Any]:
    """
    获取指定目录下的单文件插件。

    Args:
        plugin_dir (Path): 插件目录路径。
        plugin_file_suffix (str): 插件文件后缀。

    Returns:
        Generator[str, Any, Any]: 一个生成器，包括了全部的单文件型插件文件名
    """
    return (
        file.stem
        for file in plugin_dir.iterdir()
        if file.is_file() and file.name.endswith(plugin_file_suffix)
    )


def _get_directory_plugins(plugin_dir: Path) -> Generator[str, Any, Any]:
    """
    获取指定目录下的目录插件（目录插件必须包含 __init__.py）。

    Args:
        plugin_dir (Path): 插件目录路径。

    Returns:
        Generator[str, Any, Any]: 一个生成器，包括了全部的目录型插件目录名
    """
    return (
        dir.name
        for dir in plugin_dir.iterdir()
        if dir.is_dir() and (dir / "__init__.py").is_file()
    )


class SingletonMeta(type):
    """
    元类，实现单例模式。
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class PluginManager(metaclass=SingletonMeta):
    def __init__(self):
        self._loaded_plugin: dict[str, ModuleType] = (
            {}
        )  # 存放加载完毕的插件对象 键值对：ID-读取的插件对象

    def load_plugin(self, plugin_dir_path: str, plugin_file_suffix: str = ".py") -> None:
        """加载指定目录下插件，执行即为全部重新加载

        Args:
            plugin_dir (str): 插件目录路径
            plugin_file_suffix (str, optional): 插件后缀，默认".py"
        """
        self._loaded_plugin.clear()
        loaded_plugin_list: list[ModuleType] = []

        # 读取文件文件夹
        plugin_dir = Path(plugin_dir_path)

        # 无则创建
        plugin_dir.mkdir(exist_ok=True)

        plugin_instance: ModuleType

        # 加载单文件型插件
        for name in _get_single_file_plugins(plugin_dir, plugin_file_suffix):
            # 此处 name 是插件文件去除 .py 的文件名
            try:
                plugin_instance = importlib.import_module(f"{plugin_dir.name}.{name}")
                counter = 2
                while name in self._loaded_plugin:
                    name = f"{name}_{counter}"
                    counter += 1
                loaded_plugin_list.append(plugin_instance)
            except Exception as _:
                print(PLUGIN_FILE_LOAD_ERROR.format(plugin_file_name=name))
                traceback.print_exc()
                continue

        # 加载文件夹型插件
        for name in _get_directory_plugins(plugin_dir):
            # 此处 name 是插件的文件夹名
            try:
                plugin_instance = importlib.import_module(
                    f".{name}.__init__", package=plugin_dir.name
                )
                counter = 2
                while name in self._loaded_plugin:
                    name = f"{name}_{counter}"
                    counter += 1
                loaded_plugin_list.append(plugin_instance)
            except Exception as _:
                print(PLUGIN_DIR_LOAD_ERROR.format(plugin_dir_name=name))
                traceback.print_exc()
                continue

        # 读取元数据 建立 id-插件 映射
        for plugin_instance in loaded_plugin_list:
            try:
                METADATA: PluginMetadataDict = plugin_instance.METADATA
            except Exception as _:  # 如 METADATA 会 AttributeError
                traceback.print_exc()
                return

            self._loaded_plugin[METADATA["id"]] = plugin_instance

    def get_plugin_instance_by_id(self, id: str) -> ModuleType:
        """获取指定 id 的插件对象

        Args:
            id (str): id

        Returns:
            ModuleType: 插件对象
        """
        return self._loaded_plugin[id]

    def get_all_plugin_ids(self) -> list[str]:
        """获取全部加载的插件 id

        Returns:
            list[str]: 全部加载的插件 id 列表
        """
        return list(self._loaded_plugin.keys())
