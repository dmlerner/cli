#!/usr/bin/python3
import argparse

from mawk import p, parse_command, parse_command0, parse_command1, parse_command2, compose, predicate_maker

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
out_rank -= sum(map(bool)(opts))
assert out_rank >= 0


def handle_escapes(x):
    return x.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')


need_escaping = args.r, args.f, args.R, args.F
need_escaping = map(handle_escapes)(need_escaping)

p(args)


def field_type(x):
    return eval(args.t)(x) if x is not None else None


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

cmds = compose(cmds)
