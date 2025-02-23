import json
import os
import time
from datetime import datetime

import requests

RESET_COLOR = "\033[0m"


def color_builder(percentage: float, type: str) -> str:
    """根据百分比返回相应的颜色代码"""
    if percentage < 40:
        color_code = "\033[35m"
    elif percentage < 60:
        color_code = "\033[91m"
    elif percentage < 80:
        color_code = "\033[93m"
    else:
        color_code = "\033[92m"

    if type == "origin":
        color_code += f"{percentage}"
    elif type == ".2f":
        color_code += f"{percentage:.2f}"
    elif type == "<5":
        color_code += f"{percentage:<5}"
    elif type == ">5":
        color_code += f"{percentage:<5}"

    return color_code + RESET_COLOR


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

    run_counters = {}
    all_counters = {}
    wait_counters = {}

    counter_increment = lambda d, k: d.update({k: d.get(k, 0) + 1})

    with open("./temp/all.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        with open("input.txt", "w", encoding="utf-8") as f:
            for item in data["data"]:
                index = (item["id"] - 1) // 100 + 1  # index = 1 : 1-100

                counter_increment(all_counters, index)

                if item["status"] == "RUN":
                    counter_increment(run_counters, index)
                    continue

                f.write(item["url"].strip() + "\n")

                if item["status"] == "WAIT":
                    counter_increment(wait_counters, index)
                    continue

    print("  Range     RUN/TOTAL          RUN/(TOTAL-WAIT)")

    for key in sorted(run_counters.keys()):
        print(
            f"{(key-1)*100+1:>4}-{key*100:<4}:"
            f"{run_counters.get(key,0):>5}/{all_counters.get(key,0):<5}({color_builder((run_counters.get(key,0) / all_counters.get(key,0)) * 100,".2f")}%)",
            end="",
        )
        print(
            f"{run_counters.get(key,0):>5}/{all_counters.get(key,0)-wait_counters.get(key,0):<5}({color_builder((run_counters.get(key,0) / (all_counters.get(key,0)-wait_counters.get(key,0))) * 100,".2f")}%)"
        )
    total_run = sum(run_counters.values())
    total_all = sum(all_counters.values())
    total_wait = sum(wait_counters.values())
    print(
        f"Total:    {total_run:>5}/{total_all:<5}({color_builder((total_run / total_all) * 100, ".2f")}%)",
        end="",
    )
    print(
        f"{total_run:>5}/{total_all-total_wait:<5}({color_builder((total_run / (total_all-total_wait)) * 100, ".2f")}%)"
    )
    print(
        "解释： RUN/TOTAL 是不可控的，除非全部站长都能正常维持站点。此外开往维护组应尽可能提高 RUN/(TOTAL-WAIT) 的比值。"
    )


if __name__ == "__main__":
    # 记录开始时间
    start_time = time.time()
    print(f"travellings-cn-api script 开始时间：{datetime.now()}")

    main()

    # 记录结束时间
    end_time = time.time()
    print(f"travellings-cn-api script 结束时间：{datetime.now()}")

    # 计算并输出时间差
    elapsed_time = end_time - start_time
    print(f"travellings-cn-api script 运行时间：{elapsed_time:.2f} 秒")
