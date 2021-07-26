def merge_dicts(dict1, dict2):
    res = {**dict1, **dict2}

    return res


def pairwise(iterable):
    itr = iter(iterable)
    a = next(itr, None)

    for b in itr:
        yield a, b
        a = b
