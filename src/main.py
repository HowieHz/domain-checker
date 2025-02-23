import asyncio
import multiprocessing
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal, Optional, cast

import aiofiles
import tldextract
from tqdm.asyncio import tqdm_asyncio

# 用于解决运行出现 ModuleNotFoundError: No module named 'src' 问题
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/..")

from src.commands import args_parser
from src.defined_types import (
    Err,
    Ok,
    ParsedWhoisData,
    PluginMetadataDict,
    Result,
    RunArgs,
)
from src.defined_types.domain_query_result import ExceptionErrResult, MsgErrResult
from src.plugin_caller import call_async_plugin_by_id, call_sync_plugin_by_id
from src.plugin_manager import PluginManager
from src.utils.date_utils import is_datetime_expired
from src.utils.file_utils import split_file
from src.utils.logger import debug, info
from src.utils.text import (
    CLI_ERROR_INPUT_FILE_NOT_EXIST,
    CLI_ERROR_INVAID_PLUGIN_ID,
    CLI_ERROR_NO_AVAILABLE_PLUGIN,
    INFO_API_ERROR,
    INFO_CHECKING_DATE_EXPIRED,
    INFO_DATE_NOT_FOUND,
    INFO_ERROR_PARSING_DATE,
    INFO_EXPIRED,
    INFO_NOT_EXPIRED,
    INFO_NOT_REGISTER,
    INFO_REDEMPTION_PERIOD,
)


async def main_async(
    file_part: str,
    output_file: Optional[str],
    error_file: Optional[str],
    plugin_id: str,
    thread_pool_executor=ThreadPoolExecutor,
):
    """主协程函数

    Args:
        file_part (str): 要处理的文件
        output_file (Optional[str]): 输出文件的路径
        error_file (Optional[str]): 错误日志文件的路径
        thread_pool_executor (_type_, optional): 线程池实例
    """
    tasks: list[asyncio.Task | asyncio.Future] = []

    loop = asyncio.get_running_loop()

    plugin_metadata_dict: PluginMetadataDict = (
        PluginManager().get_plugin_instance_by_id(plugin_id).METADATA
    )

    extract = tldextract.TLDExtract(include_psl_private_domains=True)
    # 读取文件中的域名，一行一个域名。使用节约内存的读法
    async with aiofiles.open(file_part, "r", encoding="utf-8") as f:
        async for line in f:
            # 跳过空行
            if not line.strip():
                continue

            # 提取出域名
            extracted = extract(line.strip())
            target_domain = f"{extracted.domain}.{extracted.suffix}"

            task: asyncio.Task | asyncio.Future
            # 根据同步或异步创建 Task
            if plugin_metadata_dict["mode"] == "async":
                async_task: asyncio.Task = asyncio.create_task(
                    call_async_plugin_by_id(plugin_id, target_domain)
                )
                task = async_task
            else:
                sync_task: asyncio.Future = loop.run_in_executor(
                    thread_pool_executor, call_sync_plugin_by_id, plugin_id, target_domain
                )
                task = sync_task

            # 加入 task 列表
            tasks.append(task)

    # 等待任务完成
    for future in tqdm_asyncio.as_completed(tasks, desc="", total=len(tasks)):
        query_result: Result[ParsedWhoisData, MsgErrResult | ExceptionErrResult] = (
            await future
        )
        result_domain: str
        match query_result:
            case Err(error):
                result_domain = error["domain"]
                if "msg" in error and "code" in error:
                    error = cast(MsgErrResult, error)
                    info(
                        f"{INFO_API_ERROR}  HTTP-Status-Code:{error['code']}  Info:{error['msg']}".format(
                            domain=result_domain
                        )
                    )
                elif "err" in error:
                    error = cast(ExceptionErrResult, error)
                    info(
                        f"{INFO_API_ERROR} {str(error['err'])}".format(
                            domain=result_domain
                        )
                    )
                else:
                    raise ValueError("Invaid Data")  # 不可能的路径

                # 获取失败的写入 error.txt 文件
                if error_file is not None:
                    async with aiofiles.open(error_file, "a", encoding="utf-8") as f:
                        await f.write(result_domain + "\n")
                continue
            case Ok(parsed_whois_data):
                result_domain = parsed_whois_data["domain"]
            case _:
                raise Exception

        domain_status: tuple[
            bool, Literal["registered", "redemption", "unregistered"]
        ] = parsed_whois_data["status"]

        # debug 信息用于检查非注册状态域名的 hwhois
        if domain_status[1] != "registered":
            debug(message="parsed whois data", data=parsed_whois_data)

        if domain_status[1] == "unregistered":
            info(INFO_NOT_REGISTER.format(domain=result_domain))
            # 未注册，写入 output.txt 文件
            if output_file is not None:
                async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
                    await f.write(result_domain + "\n")
            continue
        elif domain_status[1] == "redemption":
            info(INFO_REDEMPTION_PERIOD.format(domain=result_domain))
            # 赎回期，写入 output.txt 文件
            if output_file is not None:
                async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
                    await f.write(result_domain + "\n")
            continue

        STRICT_MODE: bool = True

        def is_pass_strict_mode(domain: str) -> bool:
            """有些域名不提供域名信息，所以无法进行严格检查。检查这个域名是否允许跳过检查。

            Args:
                domain (str): 干净的域名如 a.li

            Returns:
                bool: 可跳过返回 True，不可跳过返回 False
            """
            # 有些域名不提供域名信息，所以无法进行严格检查
            if domain.endswith(".li") or domain.endswith(".ch"):
                return True
            return False

        if STRICT_MODE and not is_pass_strict_mode(domain=result_domain):
            # 严格检查
            # 为了保险，再检查下时间是否是过期的。
            # 检查“是否为赎回期”可能有缺漏，但是可以明确的是赎回期的特征：有域名过期时间但是时间过期了
            # 查询时间
            match parsed_whois_data["registry_expiry_date"]:
                case Err(datetime_paser_error):
                    # 时间解析失败
                    if datetime_paser_error["msg"] == "Error Parsing Date":
                        info(
                            f"{INFO_ERROR_PARSING_DATE} err:{datetime_paser_error['err']} raw:{datetime_paser_error['raw']}".format(
                                domain=result_domain
                            )
                        )
                    elif datetime_paser_error["msg"] == "Date not found":
                        info(
                            f"{INFO_DATE_NOT_FOUND} raw:{datetime_paser_error['raw']}".format(
                                domain=result_domain
                            )
                        )
                    else:
                        raise ValueError("Invaid Data")  # 不可能的路径

                    # 解析失败的写入 error.txt 文件
                    if error_file is not None:
                        async with aiofiles.open(error_file, "a", encoding="utf-8") as f:
                            await f.write(result_domain + "\n")
                    continue
                case Ok(expired_date):
                    pass
                case _:
                    exit(-1)

            # 计算查到的时间是否过期
            is_expired_result: Result[bool, Exception] = is_datetime_expired(expired_date)
            match is_expired_result:
                case Err(e):
                    # 在检查时间是否过期的时候出现错误
                    info(f"{INFO_CHECKING_DATE_EXPIRED} {e}".format(domain=result_domain))
                    # 解析失败的写入 error.txt 文件
                    if error_file is not None:
                        async with aiofiles.open(error_file, "a", encoding="utf-8") as f:
                            await f.write(result_domain + "\n")
                    continue
                case Ok(is_expired):
                    pass

            # 判断是否过期
            if is_expired:
                info(INFO_EXPIRED.format(domain=result_domain))
                # 已过期的写入 output.txt 文件
                if output_file is not None:
                    async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
                        await f.write(result_domain + "\n")
                continue

        # 输出未过期的
        info(INFO_NOT_EXPIRED.format(domain=result_domain))


def worker(
    file_part: str,
    output_file: Optional[str],
    error_file: Optional[str],
    max_num_threads_per_process: Optional[int],
    plugin_id: str,
):
    """一个 worker 对应一个进程，用于启动协程任务

    Args:
        file_part (str): 要处理的文件
        output_file (Optional[str]): 输出文件的路径
        error_file (Optional[str]): 错误日志文件的路径
        max_num_threads_per_process (Optional[int]): 最大线程数
    """
    with ThreadPoolExecutor(
        max_workers=max_num_threads_per_process
    ) as thread_pool_executor:
        asyncio.run(
            main_async(
                file_part=file_part,
                output_file=output_file,
                error_file=error_file,
                plugin_id=plugin_id,
                thread_pool_executor=thread_pool_executor,
            )
        )


def main(
    input_file: str,
    output_file: Optional[str],
    error_file: Optional[str],
    num_processes: int,
    max_num_threads_per_process: Optional[int],
    plugin_id: Optional[str],
):
    """主函数，用于处理输入文件并将结果输出到指定文件

    Args:
        input_file (str): 输入文件的路径
        output_file (Optional[str]): 输出文件的路径。如果为 None，则不输出结果文件
        error_file (Optional[str]): 错误日志文件的路径。如果为 None，则不输出错误日志文件
        num_processes (int): 进程数量。如果为 1，则使用单进程模式；否则使用多进程模式
        max_num_threads_per_process (Optional[int]): 每个进程的最大线程数。如果为 None，则使用默认线程数，在 Python 3.13 环境下，默认线程数为 min(32, (os.process_cpu_count() or 1) + 4)
    Raises:
        ValueError("Number of processes must be at least 1"): 进程数至少应该为 1
        ValueError("Max number of threads per process must be at least 1"): 线程数至少应该为 1
    """
    if len(PluginManager().get_all_plugin_ids()) == 0:
        raise ValueError(CLI_ERROR_NO_AVAILABLE_PLUGIN)

    if plugin_id is None:
        # 未指定插件 id
        plugin_id = "async_query"
        # 如果 async_query 不可用，就选第一个加载的插件
        if plugin_id not in PluginManager().get_all_plugin_ids():
            plugin_id = PluginManager().get_all_plugin_ids()[0]

    plugin_id = cast(str, plugin_id)

    # 检查参数是否合法
    if num_processes < 1:
        raise ValueError("Number of processes must be at least 1")
    if max_num_threads_per_process is not None and max_num_threads_per_process < 1:
        raise ValueError("Max number of threads per process must be at least 1")

    # 进程数为 1，不分割文件
    if num_processes == 1:
        worker(
            file_part=input_file,
            output_file=output_file,
            error_file=error_file,
            max_num_threads_per_process=max_num_threads_per_process,
            plugin_id=plugin_id,
        )
        return

    # 进程数 > 1 分割文件
    file_parts = split_file(input_file, num_processes)

    # 创建进程
    processes = []
    for file_part in file_parts:
        processes.append(
            multiprocessing.Process(
                target=worker,
                args=(
                    file_part,
                    output_file,
                    error_file,
                    max_num_threads_per_process,
                    plugin_id,
                ),
            )
        )

    # 启动进程
    for p in processes:
        p.start()

    # 等待进程结束
    for p in processes:
        p.join()

    # 删除临时文件
    for file_part in file_parts:
        os.remove(file_part)


if __name__ == "__main__":
    # 加载插件
    PluginManager().load_plugin(plugin_dir_path="plugins")

    # 解析命令行
    run_args: RunArgs = args_parser()

    # 确保指定的插件 id 是有效的
    if (
        run_args.plugin_id is not None
        and run_args.plugin_id not in PluginManager().get_all_plugin_ids()
    ):
        raise ValueError(CLI_ERROR_INVAID_PLUGIN_ID)

    # 确保输入文件是有效的
    input_file_instance: Path = Path(run_args.input_file)
    if not input_file_instance.exists():
        # 已自动创建
        input_file_instance.touch()
        raise FileNotFoundError(
            CLI_ERROR_INPUT_FILE_NOT_EXIST.format(input_file=run_args.input_file)
        )

    start_time: float = time.time()
    main(
        input_file=run_args.input_file,
        output_file=run_args.output_file,
        error_file=run_args.error_file,
        num_processes=run_args.num_processes,
        max_num_threads_per_process=run_args.max_num_threads_per_process,
        plugin_id=run_args.plugin_id,
    )
    end_time: float = time.time()
    info(f"Total time taken: {end_time - start_time:.3f} seconds")
