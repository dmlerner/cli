#!/usr/bin/python3
from mawk import arguments, reload
import pdb
from mawk.mawk import main
from mawk.logger import p
from mawk.utils import curry, vector, map, equal
print('test')

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


def init(cmd=None, test=''):
    global mock_stdin
    mock_stdin = MockStdin(test)
    arguments.init(cmd or ('-d',))
    reload()


def show(out):
    kept, transformed, reduced, formatted = out
    p('show', 'kept', kept, 'transformed', transformed, 'reduced', reduced, 'formatted', formatted)


def write_asserts(out):
    kept, transformed, reduced, formatted = out
    for k, v in zip('kept transformed reduced formatted'.split(), out):
        print('\tassert %s == %s' % (k, repr(v)))


class MockStdin:
    def __init__(self, x=''):
        #p('MockStdin.init, x=', x)
        self.x = x.split('\n')

    def read(self):
        return '\n'.join(self.x)

    def __iter__(self):
        return iter(self.x)


def add(x):
    return x + 1


def tst_curry():
    #from mawk import arguments
    init()
    m = map(add)
    assert m([1, 2]) == [2, 3]
    @curry
    def g(a, b):
        return a + b

    assert g(1)(2) == 3
    assert g(1, 2) == 3

    assert map(g(1))([2, 3]) == [3, 4]

    @vector
    def f(a, b, c, d=1):
        return 1000 * a + 100 * b + 10 * c + d

    p('need2')
    need2 = f(1)
    p('need1')
    need1 = need2(2)
    p('test1')
    assert need1(3) == 1231
    p('testmap')
    assert need1([7, 8]) == [1271, 1281]
    p('.....')

    @curry
    def g(a, b, c=1):
        p(a, b, c)

    g(1)(2)
    return 'pass'


def tst_dir():
    cmd = "-", "-d", '-f', '\t'
    init(cmd, dirs)
    out = kept, transformed, reduced, formatted = main(cmd, mock_stdin)
    show(out)
    foo = {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert kept == foo
    assert transformed == foo
    assert reduced == foo
    assert formatted == '0 ~/Dropbox/scripts/cli\n1 ~/Dropbox/scripts\n2 ~'
    p('done')
    return 'pass'


def tst_rp():
    cmd = "-", "-d", '-f\t', '-rp', '"Dropbox" not in V'
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    assert kept == {2: {0: '2', 1: '~'}}
    assert transformed == {2: {0: '2', 1: '~'}}
    assert reduced == {2: {0: '2', 1: '~'}}
    assert formatted == '2 ~'


def tst_cmd():
    import mawk
    cmd = '{1:2}[1]', 'sum(range(100))', '-d'
    kept, transformed, reduced, formatted = out = main(cmd)
    show(out)
    assert formatted == [2, 4950]


def tst_fp():
    cmd = "-", "-d", '-f\t', '-fp', '"Dropbox" not in V'
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    assert kept == {0: {0: '0'}, 1: {0: '1'}, 2: {0: '2', 1: '~'}}
    assert transformed == {0: {0: '0'}, 1: {0: '1'}, 2: {0: '2', 1: '~'}}
    assert reduced == {0: {0: '0'}, 1: {0: '1'}, 2: {0: '2', 1: '~'}}
    assert formatted == '0\n1\n2 ~'


def tst_ft():
    cmd = "-", "-d", '-f\t', '-ft', 'v*2'
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    assert kept == {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert transformed == {0: {0: '00', 1: '~/Dropbox/scripts/cli~/Dropbox/scripts/cli'},
                           1: {0: '11', 1: '~/Dropbox/scripts~/Dropbox/scripts'}, 2: {0: '22', 1: '~~'}}
    assert reduced == {0: {0: '00', 1: '~/Dropbox/scripts/cli~/Dropbox/scripts/cli'},
                       1: {0: '11', 1: '~/Dropbox/scripts~/Dropbox/scripts'}, 2: {0: '22', 1: '~~'}}
    assert formatted == '00 ~/Dropbox/scripts/cli~/Dropbox/scripts/cli\n11 ~/Dropbox/scripts~/Dropbox/scripts\n22 ~~'


def tst_fi():
    cmd = "-", "-d", '-f\t', '-fi', *'1 20 30'.split()
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    assert kept == {0: {1: '~/Dropbox/scripts/cli'}, 1: {1: '~/Dropbox/scripts'}, 2: {1: '~'}}
    assert transformed == {0: {1: '~/Dropbox/scripts/cli'}, 1: {1: '~/Dropbox/scripts'}, 2: {1: '~'}}
    assert reduced == {0: {1: '~/Dropbox/scripts/cli'}, 1: {1: '~/Dropbox/scripts'}, 2: {1: '~'}}
    assert formatted == '~/Dropbox/scripts/cli\n~/Dropbox/scripts\n~'


def tst_ri():
    cmd = "-", "-d", '-f\t', '-ri', *'1 20 30'.split()
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    assert kept == {1: {0: '1', 1: '~/Dropbox/scripts'}}
    assert transformed == {1: {0: '1', 1: '~/Dropbox/scripts'}}
    assert reduced == {1: {0: '1', 1: '~/Dropbox/scripts'}}
    assert formatted == '1 ~/Dropbox/scripts'

def tst_r20():
    cmd = "-", "-d", '-f\t', '-r20', 'repr(d)[::-1]'
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    assert kept == {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert transformed == {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert reduced == "}}'~' :1 ,'2' :0{ :2 ,}'stpircs/xobporD/~' :1 ,'1' :0{ :1 ,}'ilc/stpircs/xobporD/~' :1 ,'0' :0{ :0{"
    assert formatted == "}}'~' :1 ,'2' :0{ :2 ,}'stpircs/xobporD/~' :1 ,'1' :0{ :1 ,}'ilc/stpircs/xobporD/~' :1 ,'0' :0{ :0{"

def tst_r21():
    cmd = "-", "-d", '-f\t', '-r21', 'd[0]'
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    assert kept == {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert transformed == {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert reduced == {0: '0', 1: '~/Dropbox/scripts/cli'}
    assert formatted == '0\n~/Dropbox/scripts/cli'

def tst_r10():
    cmd = "-", "-d", '-f\t', '-r10', 'v[0]+"asdf"'
    init(cmd, dirs)
    kept, transformed, reduced, formatted = out = main(cmd, mock_stdin)
    show(out)
    write_asserts(out)

tests = [tst_curry, tst_dir, tst_rp, tst_cmd, tst_fp, tst_ft, tst_fi, tst_ri, tst_r20, tst_r21, tst_r10]
#tests = tests[-1:]
#tests = [tst_ft]


def test():
    init()
    for i, t in enumerate(tests):
        print('running test:', i, t)
        p(i)
        t()
        p('..............................')


if __name__ == '__main__':
    print('test.main')
    test()
    print('done')
