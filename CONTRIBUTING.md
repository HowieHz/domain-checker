# 贡献指南

## 软件发版前要做的事情

1. version.py 更新版本号

## 部署开发环境

### 在本地部署 Python3.12 环境

[Download Python](https://www.python.org/downloads/)

### 下载项目源码，并进入到项目根目录

```bash
git clone https://github.com/HowieHz/domain-checker && cd domain-checker/
```

### 创建虚拟环境

```bash
python -m venv .venv
```

### 进入虚拟环境

在 Windows 环境下

```powershell
./.venv/Scripts/activate
```

在 Bash

```bash
source ./.venv/bin/activate
```

附：退出虚拟环境的指令

```bash
deactivate
```

### 安装项目所需库

```bash
pip install -r requirements.txt
```

```bash
pip install -r requirements-dev.txt
```

创建 pre-commit 钩子，以便在每次提交前自动格式化代码

```bash
pre-commit install
```

<!-- 附：导出当前虚拟环境中的库

```bash
pip freeze > requirements.txt
``` -->

## 启用 DEBUG 模式

根据你的环境，用对应的方法设置环境变量，使得 `DEBUG_FLAG=True`

在 Bash

```bash
export DEBUG_FLAG=True
```

在 PowerShell

```powershell
$env:DEBUG_FLAG="True"
```

<!-- 查看此变量
```powershell
$env:DEBUG_FLAG
``` -->

在 CMD

```cmd
set DEBUG_FLAG=True
```

<!-- 查看此变量
```cmd
echo %DEBUG_FLAG%
``` -->


## 构建二进制文件

> 使用 nuitka 库

安装 nuitka 库

```shell
pip install nuitka
```

生成二进制文件（在 Windows 环境下）

```shell
.\build-scripts\build_with_nuitka.bat
```

生成二进制文件（在 Linux 环境下）

```bash
chmod +x ./build-scripts/build_with_nuitka.sh
./build-scripts/build_with_nuitka.sh
```

## 软件架构

### src 文件夹

`src` 文件夹包含项目的主要源代码。以下是 `src` 文件夹中各部分的作用：

- `main.py`: 项目的入口点，负责初始化和启动整个应用程序。它包含以下功能：
  - 解析命令行参数
  - 加载插件
  - 启动异步任务
  - 处理任务结果
- `commands/`: 指令模块，定义了指令参数解析器
- `plugin_manager/`: 插件管理模块，定义了单例模式的插件管理器
- `plugin_caller/`: 插件调用模块，包括调用同步型插件和异步型插件的方法
- `utils/`: 实用工具模块，包含辅助函数和工具类。这些函数和模块在项目的多个部分中被重复使用。包括：
  - 日期和时间处理函数 `date_utils`
  - 自定义类型 `defined_types`
  - 文件操作函数 `file_utils`
  - 日志函数 `logger`
  - WHOIS 解析函数 `whois_parser`
  - 项目需显示的固定文字 `text.py`

### plugins 文件夹

`plugins/`: 包含项目的插件模块。插件模块可以扩展项目的功能，通常在运行时动态加载。例如：
  - 不同的类型的查询插件

### tests 文件夹

此处包括了项目的测试文件

## 插件规范

### 基础概念解释

#### 异步型插件/同步型插件

- **异步型插件**：使用异步编程模型实现的插件。异步型插件的主函数使用 `async def` 定义，并返回一个 `PluginReturnDict` 类型的结果。
- **同步型插件**：使用同步编程模型实现的插件。同步型插件的主函数使用 `def` 定义，并返回一个 `PluginReturnDict` 类型的结果。

#### 插件用到的自定义类型

```python
from typing import Any, Literal, TypedDict


class PluginMetadataDict(TypedDict, total=False):
    """插件元数据数据类型"""

    id: str
    mode: Literal["sync", "async"]  # 标记是同步型还是异步型
    author: tuple[str] | str
    help: str


class PluginReturnDict(TypedDict):
    """插件返回值数据类型"""

    code: int
    raw: Any
```

### 单文件型插件规范

插件文件是一个以 `.py` 结尾的单文件。

需在此文件中定义常量 `METADATA`，类型为自定义类型 `PluginMetadataDict`
- "mode" 为 "async" 为异步型插件，"sync" 为同步型插件

需在此文件中定义主函数：

异步型插件的主函数签名为：
```python
async def main(domain: str) -> PluginReturnDict:
```

同步型插件的主函数签名为：
```python
def main(domain: str) -> PluginReturnDict:
```

主函数返回值说明：
- "code" 为 200 且 "raw" 非空，就会进入 WhOIS 解析检查
- "code" 为 200 但 "raw" 为空，会解析为 ⚠ Empty query result
- "code" 不为 200 时，不论 raw 怎样，均会解释为 ⚠ API Error
- 注意：如果 "raw" 不是正常的 WHOIS 内容，如 "Queried interval is too short."。请将 "code" 返回为一个非 200 的值，如 503。否则有误判为 Not Register 的可能性。

### 文件夹型插件规范

插件文件是一个文件夹。
该文件夹下要放置 `__init__.py` 文件。

此后需要在 `__init__.py` 文件中定义常量 `METADATA`，实现主函数，要求与单文件型插件一致。

### 最小样例

#### 单文件型插件最小样例

```plaintext
plugins/
└── single_file_plugin.py
```

```python
# single_file_plugin.py
from typing import TypedDict

class PluginReturnDict(TypedDict):
    code: int
    raw: str

METADATA = {
    "id": "single_file_plugin",
    "mode": "sync",  # 或 "async" 取决于插件类型
    "author": "Your Name",
    "help": "这是一个单文件型插件的最小样例",
}

# 同步模式示例
def main(domain: str) -> PluginReturnDict:
    try:
        # 查询逻辑
        # raw_whois = query(domain)
        # ...
        # if error:
        #     return {"code": 503, "raw": "query error"}
        # return {"code": 200, "raw": raw_whois}

        return {"code": 503, "raw": "Not Implemented"}
    except Exception as e:
        return {"code": 500, "raw": str(e)}

# 异步模式示例
# async def main(domain: str) -> PluginReturnDict:
#     try:
#         # 查询逻辑
#         # raw_whois = await query(domain)
#         # ...
#         # if error:
#         #     return {"code": 503, "raw": "query error"}
#         # return {"code": 200, "raw": raw_whois}
#
#         return {"code": 503, "raw": "Not Implemented"}
#     except Exception as e:
#         return {"code": 500, "raw": str(e)}
```

#### 文件夹型插件最小样例

```plaintext
plugins/
└── folder_plugin/
  └── __init__.py
```


```python
# folder_plugin/__init__.py
from typing import TypedDict

class PluginReturnDict(TypedDict):
    code: int
    raw: str

METADATA = {
    "id": "folder_plugin",
    "mode": "sync",  # 或 "async" 取决于插件类型
    "author": "Your Name",
    "help": "这是一个文件夹型插件的最小样例",
}

# 同步模式示例
def main(domain: str) -> PluginReturnDict:
    try:
        # 查询逻辑
        # raw_whois = query(domain)
        # ...
        # if error:
        #     return {"code": 503, "raw": "query error"}
        # return {"code": 200, "raw": raw_whois}

        return {"code": 503, "raw": "Not Implemented"}
    except Exception as e:
        return {"code": 500, "raw": str(e)}

# 异步模式示例
# async def main(domain: str) -> PluginReturnDict:
#     try:
#         # 查询逻辑
#         # raw_whois = await query(domain)
#         # ...
#         # if error:
#         #     return {"code": 503, "raw": "query error"}
#         # return {"code": 200, "raw": raw_whois}
#
#         return {"code": 503, "raw": "Not Implemented"}
#     except Exception as e:
#         return {"code": 500, "raw": str(e)}
```
