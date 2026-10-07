def length_of_longest_substring(s: str) -> int:
    """
    Computes the length of the longest substring without repeating characters.
    """
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
