import json
import os
import time
from datetime import datetime

import requests


def main() -> None:
    # 创建 temp 目录（如果不存在）
    os.makedirs("./temp", exist_ok=True)

    # 下载 https://api.travellings.cn/all 保存到 all.json

    url = "https://api.travellings.cn/all"
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Referer": "https://list.travellings.cn",
        },
    )
    data = response.json()
    with open("./temp/all.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 读取 all.json，将 status 不为 RUN 的 url 写入 input.txt

    with open("./temp/all.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        with open("input.txt", "w", encoding="utf-8") as f:
            for item in data["data"]:
                if item["status"] != "RUN":
                    f.write(item["url"].strip() + "\n")


if __name__ == "__main__":
    # 记录开始时间
    start_time = time.time()
    print(f"travellings-cn-api script 开始时间: {datetime.now()}")

    main()

    # 记录结束时间
    end_time = time.time()
    print(f"travellings-cn-api script 结束时间: {datetime.now()}")

    # 计算并输出时间差
    elapsed_time = end_time - start_time
    print(f"travellings-cn-api script 运行时间: {elapsed_time:.2f} 秒")
