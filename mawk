#!/usr/bin/python3
import pdb
import sys
import re
from functools import reduce, partial, wraps
import inspect

from args import field_type, args, use_stdin_py, use_stdin_raw, \
    cmds, fps, fts, ftps, rps, rts, rtps, \
    r20, r21, r10, out_rank

# Fix for broken pipe error I don't quite eunderstand
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)
_map = map


def p(*x):
    # if args.d:
    if True:
        sys.stderr.write('\n'.join(_map(str, x)) + '\n\n')


def identity(*x):
    if len(x) == 0:
        return
    if len(x) == 1:
        return x[0]
    return x


def listify(f):
    return lambda *x: list(f(*x))


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


@curry
def map(f, x):
    return list(_map(f, x))


_filter = filter
@curry
def filter(f, x):
    return list(_filter(f, x))


'''
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


def sub_all(source, *subs):
    alphanumeric = 'Q', '[a-zA-Z0-9_]'
    p('source', source)
    # replaced = False
    for sub in subs:
        for f, r in sub:
            f = f.replace(*alphanumeric)
            new = re.sub(f, r, source)
            if new != source:
                p(f, r, source, new)
                # replaced = True
            source = new
            # TODO: make default argument work with parameterized conditoin/return replaced
            # if not replaced and not set(source.lower()).intersection(set('idkv')):
            #     source = 'v ' + source
            #     p('--> ' + source)
    return source


@vector
def make_subs(prefix):
    range = r'x\.(Q+),(Q+)', r'x[x.index("\1"): x.index("\2")+1]'  # x.account_name,amount
    numeric_range = r'x([\d]+),([\d]+)', r'x[int(\1):int(\2)+1]'  # x7,9
    numeric_range_start = r'x,([\d]+)', r'x[:int(\1)+1]'  # x,9
    numeric_range_end = r'x([\d]+),', r'x[int(\1):]'  # x7,
    numeric = r'x([\d]+)', r'x[\1]'  # x7
    templates = range, numeric_range, numeric_range_start, numeric_range_end, numeric
    return map(map(replace('x', prefix)))(templates)


def flatten(xs):
    if not xs:
        return xs
    return reduce(type(xs[0]).__add__)(xs)


# def make_subs(prefixes):
    # return sum(map(_make_subs)(ps), [])


def parse_command(cmd):
    '''
    no inputs
    for i in range(10):  if i > 3:    print(i);    print(i+1)
    -->
    for i in range(10):
        if i > 3:
            print(i)
            print(i+1)
    '''
    if not cmd:
        return identity

    # TODO: make indentation less annoying? curly braces?
    cmd = cmd.replace(':', ':;')
    cmd = '\n'.join(cmd.replace('  ', '\t').split(';'))
    # dummy argument makes it work out better because signature matches the command2 case
    return lambda _: eval(cmd)


def parse_command0(cmd):
    if not cmd:
        return identity
    template = '''\
def f(k_v):
    p('parse_command0', k_v),
    k, v = k_v
    K = str(k)
    V = str(v)
    ret = %s
    p('ret', ret)
    return ret'''
    func = template % cmd
    p(func)
    exec(compile(func, '<string>', 'exec'))
    return locals()['f']


def parse_command1(cmd):
    if not cmd:
        return identity
    template = '''\
def f(di_d):
    p('parse_command1', di_d),
    if type(di_d) is dict:
        #assert False
        di_d = (None, di_d)
    i, d = di_d
    k = list(d.keys())
    K = ''.join(map(str)(k)) # TODO use args.f or similar
    v = list(d.values())
    V = ''.join(map(str)(v)) # TODO use args.f or similar
    ret = %s
    p('k, v, ret', k, v, ret)
    return ret'''
    # TODO: if foo like bar, ie any(bar in f for f in foo)
    # TODO: handle case like xi.,foo by writing find(collection, symbol) ->
    # collection[collection.index(symbol) if symbol else 0 or -1 etc]
    func = template % sub_all(cmd, flatten(make_subs('k', 'K', 'v', 'V')))
    p(func)
    exec(compile(func, '<string>', 'exec'))
    return locals()['f']


def parse_command2(cmd):
    if not cmd:
        return lambda: None
    template = '''\
def f(d):
    p('parse_command2', d),
    rk = list(d.keys())
    rK  = ''.join(map(str)(rk))
    rv = list(d.values())
    rV  = ''.join(map(str)(rv))
    ck = map(lambda d: list(d.keys()))(d.values())
    cK  = ''.join(map(str)(ck))
    cv = map(lambda d: list(d.values()))(d.values())
    cV  = ''.join(map(str)(cv))
    dv = sum(cv, [])
    dV  = ''.join(map(str)(dv))
    ret = %s
    p(rk, rv, ck, cv)
    return ret'''
    # TODO: if foo like bar, ie any(bar in f for f in foo)
    # TODO: handle case like xi.,foo by writing find(collection, symbol) ->
    # collection[collection.index(symbol) if symbol else 0 or -1 etc]

    func = template % sub_all(cmd, make_subs('rk', 'rK', 'rv', 'rV', 'ck', 'cK', 'cv', 'cV', 'dv', 'dV'))
    p(func)
    exec(compile(func, '<string>', 'exec'))
    return locals()['f']


def record_iterator(x, delim):  # TODO is this actually correct; probalby yes
    cache = []
    for line in x:
        # line += '\n'
        records = line.split(delim)
        cache.append(records[0])
        for record in records[1:]:
            if cache:
                to_yield = ''.join(cache)
                cache = [record]
                yield to_yield


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


def filter_records(records, fps, rps):
    return dict_vmap(dict_multi_filter(fps))(dict_multi_filter(rps)(records))


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


def parse(raw_records, ri_start=0):
    p('parse', repr(raw_records), ri_start)
    records = dict_vmap(index_dict)(
        dict_kmap(add(ri_start))(
            index_dict(map(map(field_type))(
                map(split(args.f, args.fx, args.fc))(
                    filter(identity)(
                        split(raw_records.strip(), args.r, args.rx, args.rc)
                    ))))))
    kept = filter_records(records, fps, rps)
    return kept


def format_output(reduced):
    if args.p:
        return repr(reduced)
    try:
        if out_rank == 2:
            if not args.fx:
                reduced = map(vmap(replace(args.f, '')))(reduced)
            reduced = vmap(join(args.F))(reduced)
            if not args.rx:
                reduced = vmap(replace(args.r, ''))(reduced)
            return join(args.R)(reduced)
        if out_rank == 1:
            if not args.rx:
                reduced = '?'
            return vmap(join(args.R))(reduced)
        return str(reduced)
    except BaseException:
        p('format_output error')
        return str(reduced)


def predicate_maker(mode, arg, vals):
    assert mode in 'wb'
    assert arg in (0, 1)
    if not vals:
        return None
    vals = set(vals)
    p(mode, arg, vals)
    return lambda xi_x: (xi_x[arg] in vals) == (mode == 'w')


def make_predicates(i, ix, v, vx):
    return filter(bool)((predicate_maker('wb'[j % 2], j // 2, vals) for j, vals in enumerate((i, ix, v, vx))))


def transform(records):
    p('records', records)
    to_transform = filter_records(records, ftps, rtps)  # TODO: reduce storage? only need keys...
    out = dict_vmap(lambda v: v.copy())(records)
    for ri in records:
        if ri in to_transform:
            for fi in records[ri]:
                if fi in to_transform[ri]:
                    # Note that fields are transformed before records, for no particularly compelling reason
                    out[ri][fi] = reduce(lambda f, ft: ft((fi, f)))(fts, out[ri][fi])
            # By design, this may crash, if rt tries to access something that wasn't kept around
            p('rts, out[ri]', rts, out[ri])
            out[ri] = reduce(lambda r, rt: rt((ri, r)))(rts, out[ri])
    p('cmds, out', cmds, out)
    out = cmds(out)
    return out


def do_reduce(rs):
    p('do_reduce', rs)
    if args.r20:
        p('r20', rs)
        return r20(rs)
    if args.r21:
        p('r21', rs)
        rs = r21(rs)
        if args.r10:
            p('r10', rs)
            rs = r10(rs)
    elif args.r10:
        p('map r10', rs)
        rs = dict_vmap(r10[0])(rs)
        if len(r10) == 2:
            rs = r10[1](rs)
    return rs


def process(records, ri_start=0):
    kept = parse(records, ri_start)
    p('kept', kept)
    transformed = transform(kept)
    p('transformed', transformed)
    reduced = do_reduce(transformed)
    p('reduced', reduced)
    formatted = format_output(reduced)
    return kept, transformed, reduced, formatted


def write_out(x):
    x = str(x).strip()
    if x:
        print(x)


if use_stdin_raw or use_stdin_py:  # TODO clean this up
    if args.s:
        for ri, raw in enumerate(record_iterator(sys.stdin, args.r)):
            if use_stdin_raw:
                kept, transformed, reduced, formatted = process(raw, ri)
                write_out(formatted)
            else:  # use_stdin_py
                out = cmds((ri, eval(raw)))
                p('out', out)
                write_out(format_output(out))
    else:
        raw = sys.stdin.read()
        if use_stdin_raw:
            kept, transformed, reduced, formatted = process(raw)
            write_out(formatted)
        else:  # use_stdin_py
            out = cmds((None, eval(raw)))
            p('out', out)
            write_out(format_output(out))
else:
    write_out(cmds(None))  # TODO is it going to be a problem that I'm passing a dummy arugment?
