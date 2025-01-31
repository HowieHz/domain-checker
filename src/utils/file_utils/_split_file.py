import os


def split_file(input_file: str, num_parts: int) -> list:
    """
    将输入文件拆分为指定数量的部分，并将它们保存为单独的文件。

    Args:
        input_file (str): 要拆分的输入文件的路径。
        num_parts (int): 要拆分的部分数量。

    Returns:
        list: 拆分部分的文件路径列表。

    Raises:
        FileNotFoundError: 如果输入文件不存在。
        ValueError: 如果 num_parts 小于或等于 0。

    Example:
        >>> split_file("example.txt", 3)
        ['./temp/temp_part_0.txt', './temp/temp_part_1.txt', './temp/temp_part_2.txt']
    """

    # 创建 temp 目录（如果不存在）
    os.makedirs("./temp", exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)
    part_size = total_lines // num_parts
    remainder = total_lines % num_parts
    file_parts = []

    start = 0
    for i in range(num_parts):
        end = start + part_size + (1 if i < remainder else 0)
        part_lines = lines[start:end]
        part_file = f"./temp/temp_part_{i}.txt"
        with open(part_file, "w", encoding="utf-8") as part_f:
            part_f.writelines(part_lines)
        file_parts.append(part_file)
        start = end

    return file_parts
