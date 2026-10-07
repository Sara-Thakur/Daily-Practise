from typing import List, Dict

def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Finds two numbers in the input array `nums` that sum up to `target`.

    :param nums: List of integers.
    :param target: Target sum integer.
    :return: Indices of the two numbers.
    """
    num_to_index: Dict[int, int] = {}
    for index, number in enumerate(nums):
        complement = target - number
        if complement in num_to_index:
            return [num_to_index[complement], index]
        num_to_index[number] = index
    return []
