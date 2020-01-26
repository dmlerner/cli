import re
from .logger import p
from .utils import vector, replace, map, compose, filter, flatten, identity, apply, const, sub
from .utils import curry  # used in eval
from .utils import find # used in make_regex_match_function_string

def make_regex_function_string(x):
    '''
    k&foo&
    k&foo(.ar)&
    k&foo&bar baz& stuff
    '''
    p('make_regex_match_function_string', x)
    if x.count('&') == 2: # TODO: what if it has multiple regexes? eg k&foo& or k&bar&
        return make_regex_match_function_string(x)
    if x.count('&') == 3:
        return make_regex_sub_function_string(x)
    assert False

def make_regex_match_function_string(x):
    '''
    'blah blah k|foo stuff asdf'
    ->
    blah blah find('foo', 'k') stuff asdf
    '''
    # TODO: allow not quoting the pattern?
    return sub(r'([^\s&]+)&([^&]+)&', 'find($2,$1)', x)

def make_regex_sub_function_string(x):
    return sub(r'([^\s&]+)&([^&]+)&([^&]*)&', 'sub($2,$3,$1)', x)

def predicate_maker(mode, arg, vals):
    assert mode in 'wb'
    assert arg in (0, 1)
    if not vals:
        return None
    vals = set(vals)
    p(mode, arg, vals)
    return lambda k, v: ([k, v][arg] in vals) == (mode == 'w')


def make_predicates(i, ix, v, vx):
    return filter(bool)((predicate_maker('wb'[j % 2], j // 2, vals) for j, vals in enumerate((i, ix, v, vx))))


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
@curry
def f(k, v):
    p('parse_command0', k, v),
    K = str(k)
    V = str(v)
    ret = %s
    p('ret', ret)
    return ret'''
    return build(template, cmd)

def build(template, cmd):
    function_text = template % cmd
    assert 'def f(' in function_text
    function_text = make_regex_function_string(function_text)
    p(function_text)
    exec(compile(function_text, '<string>', 'exec'))
    return locals()['f']


def parse_command1(cmd):
    if not cmd:
        return identity
    template = '''\
@curry
def f(i, d):
    p('parse_command1', i, d),
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
    cmd = sub_all(cmd, flatten(make_subs(['k', 'K', 'v', 'V'])))
    return build(template, cmd)


def parse_command2(cmd):
    if not cmd:
        return lambda: None
    template = '''\
def f(d):
    p('parse_command2', d, type(d)),
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

    cmd = sub_all(cmd, make_subs('rk', 'rK', 'rv', 'rV', 'ck', 'cK', 'cv', 'cV', 'dv', 'dV'))
    return build(tmeplate, cmd)

def init():
    global use_stdin_raw, use_stdin_py
    from .formatter import use_stdin_raw, use_stdin_py
    global args
    from .arguments import args

    global fps, ftps, fts
    fps = map(parse_command0)(args.fp) + make_predicates(args.fi, args.fix, args.fv, args.fvx)
    ftps = map(parse_command0)(args.ftp) + make_predicates(args.fti, args.ftix, args.ftv, args.ftvx)
    fts = map(parse_command0)(args.ft)

    global rps, rtps, rts
    rps = map(parse_command1)(args.rp) + make_predicates(args.ri, args.rix, args.rv, args.rvx)
    rtps = map(parse_command1)(args.rtp) + make_predicates(args.rti, args.rtix, args.rtv, args.rtvx)
    rts = map(parse_command1)(args.rt)

    global r20, r21, r10
    r20 = parse_command2(args.r20)
    r21 = parse_command2(args.r21)
    r10 = map(parse_command1)(args.r10)

    global cmds
    if use_stdin_raw:
        cmds = compose(map(parse_command2)(args.c[1:]))  # command1 in streaming case?
    elif use_stdin_py:
        cmds = compose(map(parse_command0)(args.c[1:]))
    else:
        cmds = const(apply(None)(map(parse_command)(args.c)))
