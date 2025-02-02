import asyncio
import re
import time

import aiohttp
import idna
from bs4 import BeautifulSoup

OUTPUT_PURE_ASCII = False  # 启用此项，最后输出的文件中均为纯 ASCII


async def fetch(session, url, semaphore):
    async with semaphore:
        async with session.get(url, timeout=60) as response:
            return await response.text()


async def main():
    iana_url = "https://www.iana.org/domains/root/db"
    tld_with_whois_server: list[tuple[str, str]] = []
    semaphore = asyncio.Semaphore(50)  # 限制协程最大并发数为 50
    connector = aiohttp.TCPConnector(limit_per_host=50)  # 限制主机的最大连接数为 50

    async with aiohttp.ClientSession(connector=connector) as session:
        res_text = await fetch(session, iana_url, semaphore)
        soup = BeautifulSoup(res_text, "html.parser")

        tlds: list[str] = [
            span_tag.get_text()
            .removeprefix("\u200f")
            .removeprefix(".")
            .removesuffix("\u200e")  # .cn -> cn
            for span_tag in soup.find_all("span", class_="domain tld")
        ]

        tasks = []
        for tld in tlds:
            # 非 unicode 的编码成 xn--
            if not tld.isascii():
                tld = idna.encode(tld).decode("ascii")

            tasks.append(
                asyncio.create_task(fetch(session, f"{iana_url}/{tld}", semaphore))
            )

        print("✅ Got all TLD")

        responses: list[str | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        for response, tld in zip(responses, tlds):
            if isinstance(response, BaseException):
                print(f"{tld} ⚠️ Error fetching: {response}")
                continue

            try:
                retxt: re.Pattern[str] = re.compile(r"<b>WHOIS Server:</b> (.*?)\n")
                arr: list[str] = retxt.findall(response)
                if arr:
                    if OUTPUT_PURE_ASCII and not tld.isascii():
                        tld = idna.encode(tld).decode("ascii")
                    tld_with_whois_server.append((tld, arr[0]))
                else:
                    print(f"{tld} hasn't WHOIS Server")
            except Exception as e:
                print(e)

    with open("whois_server_list.py", "a", encoding="utf-8") as suffix_list:
        suffix_list.write("whois_server_dict: dict[str, str] = {\n")
        for tld_and_whois_server in tld_with_whois_server:
            suffix_list.write(
                f'"{tld_and_whois_server[0]}":"{tld_and_whois_server[1]}",\n'
            )
        suffix_list.write("}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"✅ spent {time.time() - start_time:.2f} s")
