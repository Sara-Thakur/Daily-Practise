"""
Sample Generator Script for Online Coding Proctoring Assessment.

Creates 4 representative DSA coding problems with hidden test cases and populates
candidate submissions for each problem (Honest Student, Colluding Student A,
Colluding Student B with renamed variables/dead code/identical bug, and AI-Assisted Candidate).
"""

from __future__ import annotations

import json
from pathlib import Path

from models import Problem, TestCase
from proctor_engine import OnlineCodingProctorEngine


def build_sample_problems() -> list[Problem]:
    """
    Constructs 4 DSA problems complete with description, entrypoint function, and hidden test cases.

    Returns:
        List of 4 Problem objects.
    """
    problems = []

    # -------------------------------------------------------------
    # Problem 1: Two Sum
    # -------------------------------------------------------------
    prob1 = Problem(
        problem_id="prob_1_two_sum",
        title="Two Sum",
        description="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
        entrypoint="two_sum",
        test_cases=[
            TestCase("tc1_1", ([2, 7, 11, 15], 9), [0, 1], is_hidden=False),
            TestCase("tc1_2", ([3, 2, 4], 6), [1, 2], is_hidden=False),
            TestCase("tc1_3", ([3, 3], 6), [0, 1], is_hidden=True),
            TestCase("tc1_4_hidden_edge", ([-1, -2, -3, -4, -5], -8), [2, 4], is_hidden=True),
        ]
    )
    problems.append(prob1)

    # -------------------------------------------------------------
    # Problem 2: Valid Parentheses
    # -------------------------------------------------------------
    prob2 = Problem(
        problem_id="prob_2_valid_parentheses",
        title="Valid Parentheses",
        description="Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        entrypoint="is_valid",
        test_cases=[
            TestCase("tc2_1", "()[]{}", True, is_hidden=False),
            TestCase("tc2_2", "(]", False, is_hidden=False),
            TestCase("tc2_3_hidden", "{[]}", True, is_hidden=True),
            TestCase("tc2_4_hidden_edge", "((((", False, is_hidden=True),
        ]
    )
    problems.append(prob2)

    # -------------------------------------------------------------
    # Problem 3: Longest Substring Without Repeating Characters
    # -------------------------------------------------------------
    prob3 = Problem(
        problem_id="prob_3_longest_substring",
        title="Longest Substring Without Repeating Characters",
        description="Given a string `s`, find the length of the longest substring without repeating characters.",
        entrypoint="length_of_longest_substring",
        test_cases=[
            TestCase("tc3_1", "abcabcbb", 3, is_hidden=False),
            TestCase("tc3_2", "bbbbb", 1, is_hidden=False),
            TestCase("tc3_3_hidden", "pwwkew", 3, is_hidden=True),
            TestCase("tc3_4_hidden_edge", "", 0, is_hidden=True),
        ]
    )
    problems.append(prob3)

    # -------------------------------------------------------------
    # Problem 4: Binary Search in Rotated Sorted Array
    # -------------------------------------------------------------
    prob4 = Problem(
        problem_id="prob_4_rotated_search",
        title="Search in Rotated Sorted Array",
        description="Given the array `nums` after possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or -1 if it is not.",
        entrypoint="search_rotated",
        test_cases=[
            TestCase("tc4_1", ([4, 5, 6, 7, 0, 1, 2], 0), 4, is_hidden=False),
            TestCase("tc4_2", ([4, 5, 6, 7, 0, 1, 2], 3), -1, is_hidden=False),
            TestCase("tc4_3_hidden", ([1], 0), -1, is_hidden=True),
            TestCase("tc4_4_hidden_edge", ([5, 1, 3], 3), 2, is_hidden=True),
        ]
    )
    problems.append(prob4)

    return problems


def populate_sample_submissions(engine: OnlineCodingProctorEngine) -> None:
    """
    Submits 3-4 realistic candidate submissions for each problem into the assessment engine.
    Includes honest student code, colluding student pairs (renamed variables + identical bugs),
    and AI-assisted code.
    """
    # =============================================================
    # Problem 1 Submissions
    # =============================================================
    engine.submit_candidate_code(
        candidate_id="cand_101_honest",
        problem_id="prob_1_two_sum",
        code="""def two_sum(nums, target):
    seen = {}
    for idx, val in enumerate(nums):
        diff = target - val
        if diff in seen:
            return [seen[diff], idx]
        seen[val] = idx
    return []
"""
    )

    # Colluding Student A (Buggy logic on negative edge test case)
    engine.submit_candidate_code(
        candidate_id="cand_102_cheater_A",
        problem_id="prob_1_two_sum",
        code="""def two_sum(nums, target):
    # Quick brute force attempt
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n + 1): # Bug: n+1 causes IndexError on test 4!
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    )

    # Colluding Student B (Copied from A, renamed variables, added dead code statement, fails with EXACT SAME IndexError)
    engine.submit_candidate_code(
        candidate_id="cand_103_cheater_B",
        problem_id="prob_1_two_sum",
        code="""def two_sum(arr, val):
    dead_code_debug = 100 # Injected dead variable
    size = len(arr)
    for idx_a in range(size):
        for idx_b in range(idx_a + 1, size + 1): # Identical Bug copied from Cheater A!
            if arr[idx_a] + arr[idx_b] == val:
                return [idx_a, idx_b]
    return []
"""
    )

    # AI-Assisted Candidate (Generated via LLM - clean, textbook docstring, canonical structure)
    engine.submit_candidate_code(
        candidate_id="cand_104_ai_user",
        problem_id="prob_1_two_sum",
        code="""from typing import List, Dict

def two_sum(nums: List[int], target: int) -> List[int]:
    \"\"\"
    Finds two numbers in the input array `nums` that sum up to `target`.

    :param nums: List of integers.
    :param target: Target sum integer.
    :return: Indices of the two numbers.
    \"\"\"
    num_to_index: Dict[int, int] = {}
    for index, number in enumerate(nums):
        complement = target - number
        if complement in num_to_index:
            return [num_to_index[complement], index]
        num_to_index[number] = index
    return []
"""
    )

    # =============================================================
    # Problem 2 Submissions
    # =============================================================
    engine.submit_candidate_code(
        candidate_id="cand_101_honest",
        problem_id="prob_2_valid_parentheses",
        code="""def is_valid(s):
    st = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = st.pop() if st else '#'
            if mapping[char] != top:
                return False
        else:
            st.append(char)
    return not st
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_102_cheater_A",
        problem_id="prob_2_valid_parentheses",
        code="""def is_valid(s):
    stack = []
    for c in s:
        if c in '({[':
            stack.append(c)
        else:
            if not stack:
                return False
            last = stack.pop()
            if c == ')' and last != '(': return False
            if c == '}' and last != '{': return False
            if c == ']' and last != '[': return False
    return len(stack) == 0
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_103_cheater_B",
        problem_id="prob_2_valid_parentheses",
        code="""def is_valid(inp_str):
    unused_flag = True # Dead code variable
    stk = []
    for ch in inp_str:
        if ch in '({[':
            stk.append(ch)
        else:
            if not stk:
                return False
            prev = stk.pop()
            if ch == ')' and prev != '(': return False
            if ch == '}' and prev != '{': return False
            if ch == ']' and prev != '[': return False
    return len(stk) == 0
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_104_ai_user",
        problem_id="prob_2_valid_parentheses",
        code="""def is_valid(s: str) -> bool:
    \"\"\"
    Determines whether an input string of brackets is valid.
    \"\"\"
    bracket_map = {')': '(', '}': '{', ']': '['}
    stack = []
    for char in s:
        if char in bracket_map:
            top_element = stack.pop() if stack else '#'
            if bracket_map[char] != top_element:
                return False
        else:
            stack.append(char)
    return not stack
"""
    )

    # =============================================================
    # Problem 3 Submissions
    # =============================================================
    engine.submit_candidate_code(
        candidate_id="cand_101_honest",
        problem_id="prob_3_longest_substring",
        code="""def length_of_longest_substring(s):
    char_map = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        char_map[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_102_cheater_A",
        problem_id="prob_3_longest_substring",
        code="""def length_of_longest_substring(s):
    seen = set()
    l = 0
    res = 0
    for r in range(len(s)):
        while s[r] in seen:
            seen.remove(s[l])
            l += 1
        seen.add(s[r])
        res = max(res, r - l + 1)
    return res
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_103_cheater_B",
        problem_id="prob_3_longest_substring",
        code="""def length_of_longest_substring(text_data):
    dummy_counter = 0 # Dead code
    char_set = set()
    left_ptr = 0
    max_count = 0
    for right_ptr in range(len(text_data)):
        while text_data[right_ptr] in char_set:
            char_set.remove(text_data[left_ptr])
            left_ptr += 1
        char_set.add(text_data[right_ptr])
        max_count = max(max_count, right_ptr - left_ptr + 1)
    return max_count
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_104_ai_user",
        problem_id="prob_3_longest_substring",
        code="""def length_of_longest_substring(s: str) -> int:
    \"\"\"
    Computes the length of the longest substring without repeating characters.
    \"\"\"
    seen_characters = set()
    left_index = 0
    max_length = 0
    for right_index in range(len(s)):
        while s[right_index] in seen_characters:
            seen_characters.remove(s[left_index])
            left_index += 1
        seen_characters.add(s[right_index])
        max_length = max(max_length, right_index - left_index + 1)
    return max_length
"""
    )

    # =============================================================
    # Problem 4 Submissions
    # =============================================================
    engine.submit_candidate_code(
        candidate_id="cand_101_honest",
        problem_id="prob_4_rotated_search",
        code="""def search_rotated(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_102_cheater_A",
        problem_id="prob_4_rotated_search",
        code="""def search_rotated(nums, target):
    # Simple search fallback
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_103_cheater_B",
        problem_id="prob_4_rotated_search",
        code="""def search_rotated(arr, key):
    # Renamed variables version of linear scan
    temp_idx = -1
    for idx in range(len(arr)):
        if arr[idx] == key:
            return idx
    return temp_idx
"""
    )

    engine.submit_candidate_code(
        candidate_id="cand_104_ai_user",
        problem_id="prob_4_rotated_search",
        code="""from typing import List

def search_rotated(nums: List[int], target: int) -> int:
    \"\"\"
    Searches for target in a rotated sorted array using O(log N) binary search.
    \"\"\"
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
"""
    )


def generate_all_samples(engine: OnlineCodingProctorEngine) -> None:
    """
    Master function to populate all 4 DSA problems and student submissions.

    Args:
        engine: OnlineCodingProctorEngine instance.
    """
    print("==================================================")
    print("   GENERATING SAMPLE ASSESSMENT DATA")
    print("==================================================")

    problems = build_sample_problems()
    for prob in problems:
        engine.register_problem(prob)
        print(f" [+] Registered Problem: {prob.problem_id} ({prob.title}) with {len(prob.test_cases)} test cases")

    populate_sample_submissions(engine)
    print(" [+] Generated 4 Candidate Submissions for each of the 4 DSA Problems.")
    print("     - Candidate 1: Honest Student (Original Code)")
    print("     - Candidate 2: Cheater A (Buggy / Collusion Baseline)")
    print("     - Candidate 3: Cheater B (Copied from A, Renamed Variables, Dead Code, Identical Bug)")
    print("     - Candidate 4: AI User (Canonical LLM Code, Type-Hints, Std Docstrings)")
    print("==================================================\n")


if __name__ == "__main__":
    eng = OnlineCodingProctorEngine()
    generate_all_samples(eng)
