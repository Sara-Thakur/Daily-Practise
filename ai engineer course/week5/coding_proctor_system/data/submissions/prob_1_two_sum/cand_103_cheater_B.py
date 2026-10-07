def two_sum(arr, val):
    dead_code_debug = 100 # Injected dead variable
    size = len(arr)
    for idx_a in range(size):
        for idx_b in range(idx_a + 1, size + 1): # Identical Bug copied from Cheater A!
            if arr[idx_a] + arr[idx_b] == val:
                return [idx_a, idx_b]
    return []
