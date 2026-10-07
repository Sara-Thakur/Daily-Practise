def length_of_longest_substring(text_data):
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
