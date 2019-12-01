import inspect
from functools import wraps, reduce, partial
import sys


def p(*x):
    # if args.d:
    if True:
        sys.stderr.write('\n'.join(_map(str, x)) + '\n\n')


def satisfied(f, *args, **kwargs):
    try:
        p('sig, arg, kwarg', inspect.signature(f), args, kwargs)
        inspect.signature(f).bind(*args, **kwargs)
        p('returning true')
        return True
    except BaseException:
        p('returning false')
        return False


def curry(f):
    @wraps(f)
    def curried(*args, **kwargs):
        # pdb.set_trace()
        p('curried calls sat')
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


'''
def listify(f):
    return lambda *x: list(f(*x))
map = curry(map)
filter, map = map(curry, map(listify, (filter, map)))
reduce = curry(reduce)
'''


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
    return reduce(type(xs[0]).__add__)(xs)


def compose(fs):
    return lambda y: reduce(lambda y, f: f(y))(fs, y)


def check_all(fs):
    return lambda x: all(map(lambda f: f(x))(fs))


def multi_filter(fs):
    return lambda xs: filter(check_all(fs))(xs)


def dict_multi_filter(fs):
    return lambda d: dict(multi_filter(fs)(d.items()))


def dict_map(f):
    return lambda d: dict(map(f)(d.items()))


def dict_vmap(f):
    return dict_map(lambda kv: (kv[0], f(kv[1])))


def dict_kmap(f):
    return dict_map(lambda kv: (f(kv[0]), kv[1]))


def vmap(f):
    return lambda d: map(f)(d.values())


def kmap(f):
    return lambda d: map(f)(d.keys())




@curry
def split(delim='\n', remove=True, combine_consecutive=False, x=''):
    if delim is None:
        return x
    if combine_consecutive:
        while delim * 2 in x:  # TODO: speed this up
            x = x.replace(delim * 2, delim)
    for i, c in enumerate(reversed(x)):
        if c != delim:
            break
    x = x[:len(x) - i]  # remove trailing delimiters

    parts = x.split(delim)
    if not remove:
        return map(add(delim))(parts) + [parts[-1]]
    return parts


@curry
def join(delim='', x=[]):
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




