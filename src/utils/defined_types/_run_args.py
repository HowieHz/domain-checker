from typing import NamedTuple


class RunArgs(NamedTuple):
    input_file: str
    output_file: str
    error_file: str
    num_processes: int
    max_num_threads_per_process: int
