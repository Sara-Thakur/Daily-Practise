def is_valid(s):
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
