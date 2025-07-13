def find_index(lst, item):
    for i, val in enumerate(lst):
        if val == item:
            return i
    return -1