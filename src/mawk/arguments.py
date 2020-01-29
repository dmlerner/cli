#!/usr/bin/python3
import argparse
import sys
import mawk

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

parser.add_argument('-n', type=int, nargs='?')  # use only first n lines; last n if negative


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

parser.add_argument('-s', action='store_true')  # streaming
# TODO: file out

parser.add_argument('-test', nargs='?', default='')


def handle_escapes(x):
    return x.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')


#print('imported arguments')


def init(x=None, reload=True):
    global args
    #print('arguments.init', x)
    args = parser.parse_args(x or sys.argv[1:])
    args.r, args.f, args.R, args.F = map(handle_escapes, (args.r, args.f, args.R, args.F))
    #print('arguments.args, init, new: ', args)
    if reload:
        mawk.reload()


# args = parser.parse_args()
init(reload=False) # can't reload on first load
