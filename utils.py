import inspect
from functools import wraps, partial
from functools import reduce as _reduce


def satisfied(f, *args, **kwargs):
    try:
        sig = inspect.signature(f)
        sig.bind(*args, **kwargs)
        return True
    except BaseException:
        pass
    return False


def curry(f):
    @wraps(f)
    def curried(*args, **kwargs):
        if satisfied(f, *args, **kwargs):
            return f(*args, **kwargs)
        # assert args or kwargs
        return curry(partial(f, *args, **kwargs))
    return curried


_map = map
@curry
def map(f, x):
    return list(_map(f, x))


_filter = filter
@curry
def filter(f, x):
    return list(_filter(f, x))


@curry
def reduce(a, b, c):
    return _reduce(a, b, c)


@curry
def equal(a, b):
    return a == b


def vector(f):
    @wraps(f)
    def vf(*args, **kwargs):
        if satisfied(f, *args, **kwargs):
            params, domain = args[:-1], args[-1:]
            bound = partial(f, *params, **kwargs)
            if domain:
                domain = domain[0]
                if type(domain) in (list, tuple):
                    mapper = map
                elif isinstance(domain, dict):
                    mapper = dict_vmap
                else:
                    mapper = identity
                return mapper(bound)(domain)
            return bound()
        return vector(partial(f, *args, **kwargs))
    return vf


def flatten(xs):
    if not xs:
        return xs
    return reduce(type(xs[0]).__add__)(xs, xs[0])


@curry
def compose(fs, y):
    return reduce(lambda y, f: f(y))(fs, y)


@curry
def check_all(fs, x):
    return all(map(lambda f: f(x))(fs))


@curry
def multi_filter(fs, xs):
    return filter(check_all(fs))(xs)


@curry
def dict_multi_filter(fs, d):
    return dict(multi_filter(fs)(d.items()))


@curry
def dict_map(f, d):
    return dict(map(f)(d.items()))


def dict_vmap(f):  # why do I have these as one argument tuple functions? something about parse command...
    return dict_map(lambda kv: (kv[0], f(kv[1])))


def dict_kmap(f):
    return dict_map(lambda kv: (f(kv[0]), kv[1]))


@curry
def dict_v(f, d):
    return f(d.values())


@curry
def dict_k(f, d):
    return f(d.keys())


@curry
def vmap(f, d):  # aka list(dict_vmap(f).values())
    return map(f)(d.values())


@curry
def kmap(f, d):
    return map(f)(d.keys())


@curry
def split(delim, remove, combine_consecutive, x):
    if delim is None:
        return x
    if combine_consecutive:
        while delim * 2 in x:  # TODO: speed this up
            x = x.replace(delim * 2, delim)
    i = 0
    for i, c in enumerate(reversed(x)):
        if c != delim:
            break
    x = x[:len(x) - i]  # remove trailing delimiters

    parts = x.split(delim)
    if not remove:
        return map(add(delim))(parts) + [parts[-1]]
    return parts


@curry
def join(delim, x):
    return delim.join(map(str)(x))


@curry
def replace(find, replace, x):
    return x.replace(find, replace)


def index_dict(l):
    return dict(enumerate(l))


@curry
def add(a, b):
    return a + b


def identity(*x):
    if len(x) == 0:
        return
    if len(x) == 1:
        return x[0]
    return x
