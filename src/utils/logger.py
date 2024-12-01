import os, pprint
from typing import Any


DEBUG_FLAG: bool = bool(
    os.getenv("DEBUG_FLAG")
)  # 有文字都会转换成 true

if DEBUG_FLAG:
    log_stream = open("debug.log", mode="a+", encoding="utf-8")

def info(*message: str) -> None:
    quiet_flag: bool = bool(os.getenv("QUIET_FLAG"))
    is_github_workflow: bool = bool(os.getenv("GITHUB_WORKFLOW"))
    
    if is_github_workflow:
        print(f"[info]: {' '.join(message)}")
        return
    
    if quiet_flag:
        return

    print(f"[info]: {' '.join(message)}")


def debug(message: str, data: Any = "", end: str | None = "\n") -> None:
    if DEBUG_FLAG:
        log_stream.write(f"[debug]: {message}\n")
        log_stream.write(
            pprint.pformat(data, indent=4, width=160, sort_dicts=False) + "\n"
        )
