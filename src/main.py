import multiprocessing
from typing import Optional
import tldextract
import asyncio
import aiofiles
import argparse
import os

from utils.is_expired import is_expired
from utils.query_expired_date import query_expired_date
from utils.result import Ok, Err
from utils.logger import info
from utils.constant import (
    CLI_HELP_ERROR,
    CLI_HELP_INPUT,
    CLI_HELP_MESSAGE,
    CLI_HELP_NUM_PROCESSES,
    CLI_HELP_NUM_THREADS,
    CLI_HELP_OUTPUT,
    CLI_HELP_QUIET,
    CLI_HELP_UNLOCK_THREADS_LIMIT,
    DESCRIPTION,
    INFO_API_LIMIT,
    INFO_ERROR_PARSING_DATE,
    INFO_EXPIRED,
    INFO_INTERNET_ERROR,
    INFO_NOT_EXPIRED,
    INFO_NOT_FOUND_DATE,
    INFO_NOT_REGISTER,
)


async def process_domain(
    domain: str,
    output_file: Optional[str] = None,
    error_file: Optional[str] = None,
    max_num_threads_per_process: Optional[int] = None,
):
    query_expired_date_result = await query_expired_date(
        domain, max_num_threads_per_process
    )

    match query_expired_date_result:
        case Ok(value):
            expired_date = value
        case Err(error):
            if error == "Not Register":
                info(INFO_NOT_REGISTER.format(domain=domain))
                # 未注册算过期，写入 output.txt 文件
                if output_file is not None:
                    async with aiofiles.open(output_file, "a") as f:
                        await f.write(domain + "\n")
            elif error == "Not Found":
                info(INFO_NOT_FOUND_DATE.format(domain=domain))
                # 未找到的写入 error.txt 文件
                if error_file is not None:
                    async with aiofiles.open(error_file, "a") as f:
                        await f.write(domain + "\n")
            elif error == "API Limit":
                info(INFO_API_LIMIT.format(domain=domain))
                # API 限制的写入 error.txt 文件
                if error_file is not None:
                    async with aiofiles.open(error_file, "a") as f:
                        await f.write(domain + "\n")
            else:
                info(
                    (INFO_INTERNET_ERROR + error.removeprefix("Internat Error")).format(
                        domain=domain
                    )
                )
                # 解析失败的写入 error.txt 文件
                if error_file is not None:
                    async with aiofiles.open(error_file, "a") as f:
                        await f.write(domain + "\n")
            return

    is_expired_result = is_expired(expired_date)
    match is_expired_result:
        case Ok(value):
            is_expired_bool = value
        case Err(_error):
            info(INFO_ERROR_PARSING_DATE.format(domain=domain))
            # 解析失败的写入 error.txt 文件
            if error_file is not None:
                async with aiofiles.open(error_file, "a") as f:
                    await f.write(domain + "\n")
            return

    if is_expired_bool:
        info(INFO_EXPIRED.format(domain=domain))
        # 已过期的写入 output.txt 文件
        if output_file is not None:
            async with aiofiles.open(output_file, "a") as f:
                await f.write(domain + "\n")
    else:
        info(INFO_NOT_EXPIRED.format(domain=domain))


def create_parser() -> argparse.ArgumentParser:
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
        default=1,
    )
    parser.add_argument(
        "-t",
        "--max-num-threads-per-process",
        help=CLI_HELP_NUM_THREADS,
        type=int,
        default=8,
    )
    parser.add_argument(
        "-utl",
        "--unlock-threads-limit",
        help=CLI_HELP_UNLOCK_THREADS_LIMIT,
        type=str,
        nargs="?",
        const="True",  # 参数仅添加 -q 后没更参数
        metavar="True",
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
    return parser


def arg_parse():
    parser = create_parser()
    args = parser.parse_args()

    if args.quiet is not None:
        os.environ["QUIET_FLAG"] = "True"

    if args.unlock_threads_limit is not None:
        max_num_threads_per_process = None
    else:
        max_num_threads_per_process = args.max_num_threads_per_process

    if args.input is None:
        input_file = "input.txt"
    else:
        input_file = args.input

    # asyncio.run(

    # )
    main(
        input_file=input_file,
        output_file=args.output,
        error_file=args.error,
        num_processes=args.num_processes,
        max_num_threads_per_process=max_num_threads_per_process,
    )


async def process_file_part(
    file_part: str,
    output_file: Optional[str],
    error_file: Optional[str],
    max_num_threads_per_process: Optional[int],
):
    # 读取文件中的域名，一行一个域名，节约内存的读法
    async with aiofiles.open(file_part, "r") as f:
        async for line in f:
            extracted_domain = tldextract.extract(line.strip())
            domain = extracted_domain.domain + "." + extracted_domain.suffix
            await process_domain(
                domain, output_file, error_file, max_num_threads_per_process
            )


def split_file(input_file: str, num_parts: int) -> list:
    # 创建 temp 目录（如果不存在）
    os.makedirs("./temp", exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)
    part_size = total_lines // num_parts
    remainder = total_lines % num_parts
    file_parts = []

    start = 0
    for i in range(num_parts):
        end = start + part_size + (1 if i < remainder else 0)
        part_lines = lines[start:end]
        part_file = f"./temp/temp_part_{i}.txt"
        with open(part_file, "w", encoding="utf-8") as part_f:
            part_f.writelines(part_lines)
        file_parts.append(part_file)
        start = end

    return file_parts


def worker(
    file_part: str,
    output_file: Optional[str],
    error_file: Optional[str],
    max_num_threads_per_process: Optional[int],
):
    asyncio.run(
        process_file_part(
            file_part, output_file, error_file, max_num_threads_per_process
        )
    )


def main(
    input_file: str,
    output_file: Optional[str],
    error_file: Optional[str],
    num_processes: int,
    max_num_threads_per_process: Optional[int],
):
    if num_processes == 1:
        asyncio.run(
            process_file_part(
                input_file, output_file, error_file, max_num_threads_per_process
            )
        )
        return

    file_parts = split_file(input_file, num_processes)

    processes = []
    for file_part in file_parts:
        p = multiprocessing.Process(
            target=worker,
            args=(file_part, output_file, error_file, max_num_threads_per_process),
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # 删除临时文件
    for file_part in file_parts:
        os.remove(file_part)


if __name__ == "__main__":
    arg_parse()
