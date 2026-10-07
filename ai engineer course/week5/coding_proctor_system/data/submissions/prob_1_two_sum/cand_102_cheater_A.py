def two_sum(nums, target):
    # Quick brute force attempt
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n + 1): # Bug: n+1 causes IndexError on test 4!
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
