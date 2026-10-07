def search_rotated(arr, key):
    # Renamed variables version of linear scan
    temp_idx = -1
    for idx in range(len(arr)):
        if arr[idx] == key:
            return idx
    return temp_idx
