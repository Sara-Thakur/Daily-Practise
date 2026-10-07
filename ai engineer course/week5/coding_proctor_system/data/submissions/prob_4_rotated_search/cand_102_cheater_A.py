def search_rotated(nums, target):
    # Simple search fallback
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1
