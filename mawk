#!/usr/bin/python3
import pdb
import argparse
import sys
import time
import re
from functools import reduce, partial, wraps

# The problem is due to SIGPIPE handling. You can solve this problem using the following code:

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)


def identity(*x):
    if len(x) == 0:
        return
    if len(x) == 1:
        return x[0]
    return x


def listify(f):
    return lambda *x: list(f(*x))


def curry(f):
    return lambda *x: partial(f, *x)


filter, map = map(curry, map(listify, (filter, map)))
reduce = curry(reduce)


def p(*x):
    if args.d:
        sys.stderr.write('\n'.join(map(str)(x)) + '\n\n')


parser = argparse.ArgumentParser()
parser.add_argument('-d', default=False, action='store_true')  # debug output

# Delimiters
parser.add_argument('-f', default=' ', nargs='?')  # input field separator
parser.add_argument('-fc', default=True, action='store_false')  # combine consecutive delimiters
parser.add_argument('-fx', default=True, action='store_false')  # remove field separator
parser.add_argument('-F', default=' ', nargs='?')  # output field
parser.add_argument('-r', default='\n', nargs='?')  # input record
parser.add_argument('-rc', default=True, action='store_false')  # combine consecutive delimiters
parser.add_argument('-rx', default=True, action='store_false')  # remove record separator
parser.add_argument('-R', default='\n', nargs='?')  # output record

parser.add_argument('-p', default=False, action='store_true')  # output repr instead of formatted

parser.add_argument('-t', default='str', nargs='?')  # treat fields as this type


# Field flags
# Predicates to keep certain fields
parser.add_argument('-fp', default=[], nargs='*')  # p = predicate; keep these
# And helpers
parser.add_argument('-fi', default=[], nargs='*', type=int)  # index, include
parser.add_argument('-fix', default=[], nargs='*', type=int)  # index, e(x)clude
parser.add_argument('-fv', default=[], nargs='*')  # value
parser.add_argument('-fvx', default=[], nargs='*')  #

# Predicates to select fields to transform (if kept)
parser.add_argument('-ftp', default=[], nargs='*')
# And helpers
parser.add_argument('-fti', default=[], nargs='*', type=int)  # index, include
parser.add_argument('-ftix', default=[], nargs='*', type=int)  # index, e(x)clude
parser.add_argument('-ftv', default=[], nargs='*')
parser.add_argument('-ftvx', default=[], nargs='*')

# The transformations
parser.add_argument('-ft', default=[], nargs='*')  # transformation (fi, f) -> f

# Record flags
# Predicates to keep certain records, if any fields are kept
parser.add_argument('-rp', default=[], nargs='*')
# And helpers
parser.add_argument('-ri', default=[], nargs='*', type=int)
parser.add_argument('-rix', default=[], nargs='*', type=int)
parser.add_argument('-rv', default=[], nargs='*')  # value
parser.add_argument('-rvx', default=[], nargs='*')  #

# Predicates to select records to transform (if kept)
parser.add_argument('-rtp', default=[], nargs='*')
# And helpers
parser.add_argument('-rti', default=[], nargs='*', type=int)
parser.add_argument('-rtix', default=[], nargs='*', type=int)
parser.add_argument('-rtv', default=[], nargs='*')
parser.add_argument('-rtvx', default=[], nargs='*')

# The transformations
parser.add_argument('-rt', default=[], nargs='*')  # (ri, { fi: f }) -> { fi: f' }. Should generally preserve {fi}
# The reductions for after transformation
# TODO: defaults that just args.R.join etc if flag provided without value (do nothing if no flag at al)
parser.add_argument('-r21', nargs='?')  # { ri: { fi: f} } -> { k: v }
parser.add_argument('-r10', default=[], nargs='*')  # { k: v } -> v
parser.add_argument('-r20', nargs='?')  # { ri: { fi: f} } -> v


# if c[0] is '-', use stdin
# f({ri}, {fi}, {f}), eg: f02 + sum(ri)
parser.add_argument('c', nargs='*')

# brief; allows omitting _ in predicate variable names
parser.add_argument('-b', action='store_false')

# TODO: field/record transformations before cmd?

parser.add_argument('-s', action='store_true')  # streaming
# TODO: file out

args = parser.parse_args()

out_rank = 2
if args.r20:
    assert not args.r21 and not args.r10
    out_rank = 0
opts = (args.r21, *args.r10)
boolmap = map(bool)
summand = boolmap(opts)
out_rank -= sum(summand)
assert out_rank >= 0


def handle_escapes(x):
    x = x.replace('\\n', '\n')
    x = x.replace('\\r', '\r')
    x = x.replace('\\t', '\t')
    return x


args.r = handle_escapes(args.r)
args.f = handle_escapes(args.f)
args.R = handle_escapes(args.R)
args.F = handle_escapes(args.F)

p(args)


def field_type(x):
    return eval(args.t)(x) if x is not None else None


def sub_all(source, *subs):
    alphanumeric = 'Q', '[a-zA-Z0-9_]'
    p('source', source)
    replaced = False
    for sub in subs:
        for f, r in sub:
            f = f.replace(*alphanumeric)
            new = re.sub(f, r, source)
            if new != source:
                p(f, r, source, new)
                replaced = True
            source = new
            # TODO: make default argument work with parameterized conditoin/return replaced
        # if not replaced and not set(source.lower()).intersection(set('idkv')):
            #source = 'v ' + source
            #p('--> ' + source)
    return source


def _make_subs(prefix):
    range = r'x\.(Q+),(Q+)', r'x[x.index("\1"): x.index("\2")+1]'  # x.account_name,amount
    numeric_range = r'x([\d]+),([\d]+)', r'x[int(\1):int(\2)+1]'  # x7,9
    numeric_range_start = r'x,([\d]+)', r'x[:int(\1)+1]'  # x,9
    numeric_range_end = r'x([\d]+),', r'x[int(\1):]'  # x7,
    numeric = r'x([\d]+)', r'x[\1]'  # x7
    templates = range, numeric_range, numeric_range_start, numeric_range_end, numeric
    return map(lambda template:
               map(lambda fr: fr.replace('x', prefix))(template)
               )(templates)


def make_subs(*ps):
    return reduce(list.__add__)(map(_make_subs)(ps))


def catch_exceptions(f):  # too heavy handed. instead default value syntax?
    f.errors = 0
    f.total = 0

    @wraps(f)
    def catches_exceptions(*args, **kwargs):
        try:
            f.total += 1
            return f(*args, **kwargs)
        except BaseException:
            f.errors += 1
            error_ratio = f.errors / f.total
            if f.total > 10 and error_ratio > .1:
                p('error ratio for %s is %s (%s / %s)' % (f, error_ratio, f.errors, f.total))
    return catches_exceptions


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
    func = template % sub_all(cmd, make_subs('k', 'K', 'v', 'V'))
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


# Test data
dirs = '''\
0\t~/Dropbox/scripts/cli
1\t~/Dropbox/scripts
2\t~'''

dicts = '''\
<a:1, b:2>
<c:3, d:4>
<e:5, f:6, g:7>
'''

nums = '1,2;3,4;;;;;5,6;7,8;;;'


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


def split(x, delim, remove=True, combine_consecutive=False):
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
        return map(lambda p: p + delim)(parts) + [parts[-1]]
    return parts

@curry
def join(delim='', x=[]):
    return delim.join(map(str)(x))


def index_dict(l):
    return dict(enumerate(l))


def parse(raw_records, ri_start=0):
    p('parse', repr(raw_records), ri_start)
    records = dict_vmap(index_dict)(
        dict_kmap(lambda k: k + ri_start)(
            index_dict(map(map(field_type))(
                map(lambda r: split(r, args.f, args.fx, args.fc))(
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
            return join(args.R)(vmap(join(args.F))(reduced))
        if out_rank == 1:
            return args.R.join(map(str)(reduced.values()))
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


fps = map(parse_command0)(args.fp) + make_predicates(args.fi, args.fix, args.fv, args.fvx)
ftps = map(parse_command0)(args.ftp) + make_predicates(args.fti, args.ftix, args.ftv, args.ftvx)
fts = map(parse_command0)(args.ft)

rps = map(parse_command1)(args.rp) + make_predicates(args.ri, args.rix, args.rv, args.rvx)
rtps = map(parse_command1)(args.rtp) + make_predicates(args.ri, args.rix, args.rv, args.rvx)
rts = map(parse_command1)(args.rt)

r20 = parse_command2(args.r20)
r21 = parse_command2(args.r21)
r10 = map(parse_command1)(args.r10)

use_stdin_raw = args.c and args.c[0] == '-'
use_stdin_py = args.c and args.c[0] == '.'
if use_stdin_raw:
    cmds = map(parse_command2)(args.c[1:])  # command1 in streaming case?
elif use_stdin_py:
    cmds = map(parse_command0)(args.c[1:])
else:
    cmds = map(parse_command)(args.c)  # compose probably doens't work here, zero args...

p('stdinmode', use_stdin_raw, use_stdin_py)
cmds = compose(cmds)


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
