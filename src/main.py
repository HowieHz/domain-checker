import logging
import tldextract
import asyncio
import aiofiles

from utils.is_expired import is_expired
from utils.query_expired_date import query_expired_date
from utils.result import Ok, Err
from utils.version import VERSION

async def process_domain(domain):
    query_expired_date_result = await query_expired_date(domain)
    
    match query_expired_date_result:
        case Ok(value):
            expired_date = value
        case Err(_error):
            print(domain, "未找到过期日期")
            # 未找到的写入 error.txt 文件
            async with aiofiles.open("error.txt", "a") as f:
                await f.write(domain + "\n")
            return
    
    is_expired_result = is_expired(expired_date)
    match is_expired_result:
        case Ok(value):
            is_expired_bool = value
        case Err(_error):
            print(domain, "日期解析失败")
            # 解析失败的写入 error.txt 文件
            async with aiofiles.open("error.txt", "a") as f:
                await f.write(domain + "\n")
            return

    if is_expired_bool:
        print(domain, "已过期")
        # 已过期的写入 output.txt 文件
        async with aiofiles.open("output.txt", "a") as f:
            await f.write(domain + "\n")
    else:
        print(domain, "未过期")

async def main():
    logging.basicConfig(level=logging.ERROR)
    # 读取 input.txt 文件中的域名，一行一个域名，节约内存的读法
    async with aiofiles.open("input.txt", "r") as f:
        async for line in f:
            extracted_domain = tldextract.extract(line.strip())
            domain = extracted_domain.domain + "." + extracted_domain.suffix
            await process_domain(domain)

if __name__ == "__main__":
    print("version:", VERSION)
    asyncio.run(main())