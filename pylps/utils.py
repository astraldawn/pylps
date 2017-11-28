def strictly_increasing(iterable):
    return all(x < y for x, y in zip(iterable, iterable[1:]))
