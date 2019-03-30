def is_not_blank(s):
    return bool(s and s.strip())


def is_blank(s):
    return not is_not_blank(s)


def str_2_bool(v):
    if is_blank(v):
        return False
    else:
        return v.lower() == "true"
