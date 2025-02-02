import argparse
import os
from typing import Optional

from plugin_manager._plugin_manger import PluginManager
from utils.defined_types import RunArgs
from utils.text import (
    CLI_HELP_ERROR,
    CLI_HELP_INPUT,
    CLI_HELP_MESSAGE,
    CLI_HELP_NUM_PROCESSES,
    CLI_HELP_NUM_THREADS,
    CLI_HELP_OUTPUT,
    CLI_HELP_PLUGIN_ID,
    CLI_HELP_QUIET,
    DESCRIPTION,
)


def _create_command_parser() -> argparse.ArgumentParser:
    prefix_chars: str = "-"
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, add_help=False, prefix_chars=prefix_chars
    )

    default_prefix = "-" if "-" in prefix_chars else prefix_chars[0]
    parser.add_argument(
        default_prefix + "h",
        default_prefix * 2 + "help",
        action="help",
        default="==SUPPRESS==",
        help=CLI_HELP_MESSAGE,
    )

    parser.add_argument("-i", "--input", help=CLI_HELP_INPUT, type=str)
    parser.add_argument("-o", "--output", help=CLI_HELP_OUTPUT, type=str)
    parser.add_argument("-e", "--error", help=CLI_HELP_ERROR, type=str)
    parser.add_argument(
        "-p",
        "--num-processes",
        help=CLI_HELP_NUM_PROCESSES,
        type=int,
    )
    parser.add_argument(
        "-t",
        "--max-num-threads-per-process",
        help=CLI_HELP_NUM_THREADS,
        type=int,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help=CLI_HELP_QUIET,
        type=str,
        nargs="?",
        const="True",  # 参数仅添加 -q 后没更参数
        metavar="True",
    )
    parser.add_argument(
        "-id",
        help=CLI_HELP_PLUGIN_ID.format(
            ids=",".join(PluginManager().get_all_plugin_ids())
        ),
        type=str,
    )
    return parser


def args_parser() -> RunArgs:
    """解析命令行参数，并且按需写入环境变量

    Returns:
        RunArgs: 用于调用主程序的参数
    Raises:
        TypeError: 参数类型不正确
    """
    # 创建命令解析器并且调用 parse_args 方法解析传入的命令
    args = _create_command_parser().parse_args()

    # 读取“安静模式”参数
    if args.quiet is not None:
        os.environ["QUIET_FLAG"] = "True"

    # 读取剩余参数
    input_file: str = "input.txt" if args.input is None else str(args.input)
    output_file: Optional[str] = args.output
    error_file: Optional[str] = args.error
    num_processes: int = 1 if args.num_processes is None else int(args.num_processes)
    max_num_threads_per_process: Optional[int] = args.max_num_threads_per_process
    plugin_id: Optional[str] = args.id

    # argparse 设置了 type，参数就会自动格式化为对应 type，但是这里还是特检一次
    for var, var_type in [
        (input_file, str),
        (output_file, (str, type(None))),
        (error_file, (str, type(None))),
        (num_processes, int),
        (max_num_threads_per_process, (int, type(None))),
        (plugin_id, (str, type(None))),
    ]:
        if not isinstance(var, var_type):
            raise TypeError(f"{var} must be of type {var_type}")

    return RunArgs(
        input_file=input_file,
        output_file=output_file,
        error_file=error_file,
        num_processes=num_processes,
        max_num_threads_per_process=max_num_threads_per_process,
        plugin_id=plugin_id,
    )
