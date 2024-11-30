import os

def info(*message: str) -> None:
    quiet_flag: bool = bool(os.getenv("QUIET_FLAG"))

    if quiet_flag:
        return

    print(f"[info]: {' '.join(message)}")