from .utils import dict_kmap, dict_vmap, index_dict, \
    add, split, identity, replace, map, filter, join, dict_v
from .logger import p
from . import arguments
#print('formatter')


def parse(raw_records, ri_start=0):
    p('parse', raw_records, repr(raw_records), ri_start)
    records = dict_vmap(index_dict)(
        dict_kmap(add(ri_start))(
            index_dict(map(map(field_type))(
                map(split(arguments.args.fl, arguments.args.f))(
                    filter(identity)(
                        split(arguments.args.rl, arguments.args.r, raw_records))
                    )))))
    return records


def field_type(x):
    return eval(arguments.args.t)(x) if x is not None else None


def get_input(stdin):
    p('get_input, arguments.args.test = ', arguments.args.test, stdin)
    it = record_iterator(stdin, arguments.args.r)
    if arguments.args.s:
        return it
    return stdin.read()
    x = list(it)
    p(x)
    return arguments.args.r.join(x)
    # return arguments.args.r.join(list(it))


def record_iterator(x, delim):
    cache = []
    for line in x:
        #p('line', repr(line))
        # line += '\n'
        records = line.split(delim)
        cache.append(records[0])
        for record in records[1:]:
            if cache:
                to_yield = ''.join(cache)
                cache = [record]
                yield to_yield


def format_output(reduced):
    p(reduced)
    if arguments.args.p:
        return repr(reduced)
    try:
        if out_rank == 0:
            return str(reduced)
        if out_rank == 2:
            if not arguments.args.fx:
                reduced = dict_vmap(dict_vmap(replace(arguments.args.f, '')))(reduced)
                p(reduced)
            reduced = dict_vmap(dict_v(join(arguments.args.F)))(reduced)
            p(reduced)
        if not arguments.args.rx:
            reduced = dict_vmap(replace(arguments.args.r, ''))(reduced)
            p(reduced)
        return dict_v(join(arguments.args.R))(reduced)
    except BaseException:
        p('format_output error')
        return str(reduced)


def write_out(x):
    x = str(x).strip()
    if x:
        print(x)


def get_out_rank(args):
    out_rank = 2
    if arguments.args.r20:
        assert not arguments.args.r21 and not arguments.args.r10
        out_rank = 0
    opts = (arguments.args.r21, *arguments.args.r10)
    out_rank -= sum(map(bool)(opts))
    assert out_rank >= 0
    return out_rank


#print('formatter, arguments.args', arguments.args)
use_stdin_raw = arguments.args.c and arguments.args.c[0] == '-'
use_stdin_py = arguments.args.c and arguments.args.c[0] == '.'
out_rank = get_out_rank(arguments.args)
