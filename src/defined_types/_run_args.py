from typing import NamedTuple, Optional


class RunArgs(NamedTuple):
    input_file: str
    output_file: Optional[str]
    error_file: Optional[str]
    num_processes: int
    max_num_threads_per_process: Optional[int]
    plugin_id: Optional[str]
