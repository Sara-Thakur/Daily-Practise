def is_valid(s: str) -> bool:
    """
    Determines whether an input string of brackets is valid.
    """
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
