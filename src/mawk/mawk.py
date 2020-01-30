#!/usr/bin/python3
#print('mawk')
from .utils import reduce, dict_vmap, dict_multi_filter, compose, apply, vmap, dict_map, splat, dict_dmap
from .functionmaker import ftps, rtps, fts, rts, cmds, r20, r21, r10, fps, rps
from . import formatter
from .formatter import parse, format_output
from .formatter import use_stdin_raw, use_stdin_py, get_input, write_out, format_output
from .logger import p
from . import arguments
import sys
import pdb


def filter_records(records, fps, rps):
    p('filter_records', records, fps, rps)
    return dict_vmap(dict_multi_filter(fps))(dict_multi_filter(rps)(records))


def transform(records):
    p('records', records)
    to_transform = filter_records(records, ftps, rtps)  # TODO: reduce storage? only need keys...
    out = dict_vmap(lambda v: v.copy())(records)
    # TODO: use dict.update to avoid loops?
    # TODO: skip when there are no rts/fts?
    for ri in records:
        if ri in to_transform:
            for fi in records[ri]:
                if fi in to_transform[ri]:
                    # Note that fields are transformed before records, for no particularly compelling reason
                    out[ri][fi] = compose(map(apply(fi), fts))(out[ri][fi])
            # By design, this may crash, if rt tries to access something that wasn't kept around
            p('rts, out[ri]', rts, out[ri])
            out[ri] = compose(map(apply(ri), rts))(out[ri])
    p('cmds, out', cmds, out)
    out = cmds(out)
    return out


def do_reduce(rs):
    p('do_reduce', rs)
    if arguments.args.r20:
        p('r20', rs)
        return r20(rs)
    if arguments.args.r21:
        p('r21', rs)
        rs = r21(rs)
        if arguments.args.r10:
            p('r10', rs)
            rs = r10(rs)
    elif arguments.args.r10:
        p('map r10', rs, r10)
        #F = splat(r10[0])
        F = r10[0]
        rsmapper = dict_dmap(F)
        rs = rsmapper(rs)
        if len(r10) == 2:
            p('len 2 r10')
            rs = r10[1](rs)
    return rs


def process(records, ri_start=0):
    p('process', records)
    records = parse(records, ri_start)
    kept = filter_records(records, fps, rps)
    p('kept', kept)
    transformed = transform(kept)
    p('transformed', transformed)
    reduced = do_reduce(transformed)
    p('reduced', reduced)
    formatted = format_output(reduced)
    return kept, transformed, reduced, formatted


def main(raw_args=None, stdin=None):
    #print('mawk.main', raw_args, arguments.args, stdin and stdin.x)
    if raw_args:
        arguments.init(raw_args)
    stdin = stdin or sys.stdin
    if formatter.use_stdin_raw or formatter.use_stdin_py:  # TODO clean this up
        if arguments.args.s:
            for ri, raw in enumerate(get_input(stdin)):
                if use_stdin_raw:
                    kept, transformed, reduced, formatted = process(raw, ri)
                    write_out(formatted)
                    return kept, transformed, reduced, formatted
                else:  # use_stdin_py
                    out = cmds((ri, eval(raw)))
                    p('out', out)
                    formatted = format_output(out)
                    write_out(formatted)
                    return None, None, None, formatted
        else:
            raw = get_input(stdin)
            if use_stdin_raw:
                kept, transformed, reduced, formatted = process(raw)
                write_out(formatted)
                return kept, transformed, reduced, formatted
            else:  # use_stdin_py
                evaled = eval(raw)
                out = cmds(evaled)
                formatted = format_output(out)
                write_out(formatted)
                return None, None, None, formatted
    else:
        out = cmds(None)
        write_out(out)  # TODO is it going to be a problem that I'm passing a dummy arugment?
        return None, None, None, out
#cat offline.log | m - -rp 'V&"AttributionPlatformSyncTest|GacsAt"&' | m - -r10 'V&".*\((.*)"&"$1"&' -d > foo
