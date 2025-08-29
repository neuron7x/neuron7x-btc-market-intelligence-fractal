def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)
