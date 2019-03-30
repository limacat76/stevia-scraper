def is_not_blank(s):
    return bool(s and s.strip())


def is_blank(s):
    return not is_not_blank(s)


def str_2_bool(v):
    if is_blank(v):
        return False
    else:
        return v.lower() == "true"


def extract(d, keys):
    return dict((k, d[k]) for k in keys if k in d)


def to_dict(item):
    try:
        if isinstance(item, dict):
            result = item
        else:
            result = vars(item)
    except TypeError:
        result = item

    return result
