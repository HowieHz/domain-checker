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
        case Err(_error):
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


async def main(
    input_file: str,
    output_file: Optional[str] = None,
    error_file: Optional[str] = None,
):
    # 读取 input.txt 文件中的域名，一行一个域名，节约内存的读法
    async with aiofiles.open(input_file, "r") as f:
        async for line in f:
            extracted_domain = tldextract.extract(line.strip())
            domain = extracted_domain.domain + "." + extracted_domain.suffix
            await process_domain(domain, output_file, error_file)


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

    asyncio.run(
        main(input_file=input_file, output_file=args.output, error_file=args.error)
    )


if __name__ == "__main__":
    arg_parse()
