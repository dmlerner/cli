import inspect
import sys
import pdb
from args import args

outfile = open('out.txt', 'w')


def get_location(n=2):
    stack = inspect.stack()
    s = stack[n]
    filename = s.filename
    context = s.code_context and s.code_context[0] or 'None'
    if 'david' not in filename:
        return
    filename = filename[('/' + filename).rindex('/'):]
    return ' '.join(str(x).strip() for x in (filename, context, s.lineno))


def trace():
    n = len(inspect.stack())
    location = '\n'.join(filter(bool, map(get_location, range(n))))
    return location


def p(*x, d=False):
    if d:
        pdb.set_trace()
    if args.d:
        log = '\n'.join(map(str, x)) + '\n\n'
        sys.stderr.write(log)
        outfile.write(log)


p(args)
