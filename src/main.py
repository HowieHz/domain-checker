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
    CLI_HELP_OUTPUT,
    CLI_HELP_QUIET,
    DESCRIPTION,
)


async def process_domain(
    domain: str, output_file: Optional[str] = None, error_file: Optional[str] = None
):
    query_expired_date_result = await query_expired_date(domain)

    match query_expired_date_result:
        case Ok(value):
            expired_date = value
        case Err(error):
            if error == "Not Register":
                info(domain, "未注册")
                # 未注册算过期，写入 output.txt 文件
                if output_file is not None:
                    async with aiofiles.open(output_file, "a") as f:
                        await f.write(domain + "\n")
            elif error == "Not Found":
                info(domain, "未找到过期日期")
                # 未找到的写入 error.txt 文件
                if error_file is not None:
                    async with aiofiles.open(error_file, "a") as f:
                        await f.write(domain + "\n")
            return

    is_expired_result = is_expired(expired_date)
    match is_expired_result:
        case Ok(value):
            is_expired_bool = value
        case Err(_error):
            info(domain, "日期解析失败")
            # 解析失败的写入 error.txt 文件
            if error_file is not None:
                async with aiofiles.open(error_file, "a") as f:
                    await f.write(domain + "\n")
            return

    if is_expired_bool:
        info(domain, "已过期")
        # 已过期的写入 output.txt 文件
        if output_file is not None:
            async with aiofiles.open(output_file, "a") as f:
                await f.write(domain + "\n")
    else:
        info(domain, "未过期")

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
        "-n",
        "--num-processes",
        help=CLI_HELP_NUM_PROCESSES,
        type=int,
        default=4,
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

    if args.input is None:
        input_file = "input.txt"
    else:
        input_file = args.input

    # asyncio.run(
        
    # )
    main(input_file=input_file, output_file=args.output, error_file=args.error, num_processes=args.num_processes)

async def process_file_part(file_part: str, output_file: Optional[str], error_file: Optional[str]):
    # 读取文件中的域名，一行一个域名，节约内存的读法
    async with aiofiles.open(file_part, "r") as f:
        async for line in f:
            extracted_domain = tldextract.extract(line.strip())
            domain = extracted_domain.domain + "." + extracted_domain.suffix
            await process_domain(domain, output_file, error_file)

def split_file(input_file: str, num_parts: int) -> list:
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    part_size = len(lines) // num_parts
    file_parts = []

    for i in range(num_parts):
        part_lines = lines[i * part_size: (i + 1) * part_size]
        part_file = f"./temp/temp_part_{i}.txt"
        with open(part_file, "w", encoding="utf-8") as part_f:
            part_f.writelines(part_lines)
        file_parts.append(part_file)

    return file_parts

def worker(file_part: str, output_file: Optional[str], error_file: Optional[str]):
    asyncio.run(process_file_part(file_part, output_file, error_file))

def main(input_file: str, output_file: Optional[str], error_file: Optional[str], num_processes: int):
    file_parts = split_file(input_file, num_processes)

    processes = []
    for file_part in file_parts:
        p = multiprocessing.Process(target=worker, args=(file_part, output_file, error_file))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    arg_parse()
