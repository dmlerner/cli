from logger import p
import sys
from utils import dict_kmap, dict_vmap, index_dict, \
    add, split, identity, replace, map, filter, join, dict_v


def parse(raw_records, ri_start=0):
    p('parse', raw_records, repr(raw_records), ri_start)
    records = dict_vmap(index_dict)(
        dict_kmap(add(ri_start))(
            index_dict(map(map(field_type))(
                map(split(args.f, args.fx, args.fc))(
                    filter(identity)(
                        split(args.r, args.rx, args.rc, raw_records.strip())
                    ))))))
    return records


def field_type(x):
    return eval(args.t)(x) if x is not None else None


def get_input(stdin):
    p('get_input, args.test = ', args.test, stdin)
    it = record_iterator(stdin, args.r)
    if args.s:
        return it
    return stdin.read()
    x = list(it)
    p(x)
    return args.r.join(x)
    #return args.r.join(list(it))


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
    if args.p:
        return repr(reduced)
    try:
        if out_rank == 0:
            return str(reduced)
        if out_rank == 2:
            if not args.fx:
                reduced = dict_vmap(dict_vmap(replace(args.f, '')))(reduced)
                p(reduced)
            reduced = dict_vmap(dict_v(join(args.F)))(reduced)
            p(reduced)
        if not args.rx:
            reduced = dict_vmap(replace(args.r, ''))(reduced)
            p(reduced)
        return dict_v(join(args.R))(reduced)
    except BaseException:
        p('format_output error')
        return str(reduced)


def write_out(x):
    x = str(x).strip()
    if x:
        print(x)


def get_out_rank(args):
    out_rank = 2
    if args.r20:
        assert not args.r21 and not args.r10
        out_rank = 0
    opts = (args.r21, *args.r10)
    out_rank -= sum(map(bool)(opts))
    assert out_rank >= 0
    return out_rank


def init():
    global use_stdin_raw, use_stdin_py, out_rank, args
    from arguments import args
    use_stdin_raw = args.c and args.c[0] == '-'
    use_stdin_py = args.c and args.c[0] == '.'
    out_rank = get_out_rank(args)
