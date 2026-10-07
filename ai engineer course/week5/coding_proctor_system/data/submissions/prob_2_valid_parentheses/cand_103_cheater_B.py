def is_valid(inp_str):
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
