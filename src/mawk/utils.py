import re
from functools import reduce as _reduce
from functools import wraps, partial
import inspect
from builtins import map, filter  # guards against reload bugs


def satisfied(f, *args, **kwargs):
    # TODO/wip: if too many args, fail
    sig = inspect.signature(f)
    assert len(args) + len(kwargs) <= len(sig.parameters)
    # TODO: what if varargs etc? no real upper bound on param list length...
    try:
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


def const(a):
    return lambda *args, **kwargs: a


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


@vector
def apply(x, f):
    # pdb.set_trace()
    return f(x)


@curry
def flip(f, a, b):
    return f(b, a)


def rotate(f):
    return lambda *args, **kwargs: f(args[-1], *args[:-1], **kwargs)


def flatten(xs):
    if not xs:
        return xs
    return reduce(type(xs[0]).__add__)(xs, xs[0])


@curry
def compose(fs, y):
    return reduce(apply, fs, y)


@curry
def check_all(fs, x):
    return all(map(apply(x), fs))


@curry
def multi_filter(fs, xs):
    return filter(check_all(fs))(xs)


@curry
def dict_multi_filter(fs, d):
    # this broke because we're passing fs:: [f(k, v)], but multi_filter expects fs:: [f(v)]
    return dict(multi_filter(map(splat, fs))(d.items()))


@curry
def dict_map(f, d):
    return dict(map(f)(d.items()))


def dict_vmap(f):
    '''why would f take one arg?
       answer: because it's convenient to take an element of d.items'''
    return dict_map(lambda kv: (kv[0], f(kv[1])))

#def dict_vmap(f):
    #return dict_dmap(lambda kv: f(kv[1]))


def dict_kmap(f):
    return dict_map(lambda kv: (f(kv[0]), kv[1]))

def dict_dmap(f):
    return dict_map(lambda kv: (kv[0], f(*kv))) # TODO: generalize these dict_.*maps


@curry
def dict_v(f, d):
    return f(d.values())


@curry
def dict_k(f, d):
    return f(d.keys())


@curry
def vmap(f, d):
    return map(f)(d.values())


@curry
def kmap(f, d):
    return map(f)(d.keys())

@curry
def regex_split(pattern, x):
    return re.split(pattern, x)


def split(lead, pattern, x):
    parts = re.split('(%s)' % pattern, x)
    parts.insert(0 if lead else -1, '')
    return list(filter(bool, [a+b for a,b in zip(parts[::2], parts[1::2])]))

@curry
def split_lead(pattern, x):
    return split(True, pattern, x)

@curry
def split_trail(pattern, x):
    return split(False, pattern, x)

@curry
def _split(delim, remove, combine_consecutive, x):
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


def unsplat(f):  # TODO: think about kwargs
    return lambda *args: f(args)


def splat(f):
    return lambda x: f(*x)

@curry
def find(pattern, string):
        found = re.findall(pattern, string)  # find all matches anywhere, consuming l->r
        if not found:
            return
        if len(found) == 1:
            return found[0]
        return found

@curry
def sub(pattern, repl, string):
	repl = re.sub(r'\$(.)', r'\\g<\g<1>>', repl) # use $1 instead of \g<1>
	return re.sub(pattern, repl, string)
