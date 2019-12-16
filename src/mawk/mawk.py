#!/usr/bin/python3
from .utils import reduce, dict_vmap, dict_multi_filter, compose, apply
from .formatter import parse, format_output
from .logger import p
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
        p('map r10', rs, r10)
        rs = dict_vmap(r10[0])(rs)
        if len(r10) == 2:
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


def init():
    global ftps, rtps, fts, rts, cmds, r20, r21, r10, fps, rps, args
    from .functionmaker import ftps, rtps, fts, rts, cmds, r20, r21, r10, fps, rps
    from .arguments import args
