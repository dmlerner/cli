#!/usr/bin/python3
from mawk.utils import curry, vector, map, equal
from mawk.logger import p
import pdb
from mawk import arguments

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


def test_curry():
    global args
    from mawk import arguments
    arguments.init('-d')
    from mawk.arguments import args
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


def test_dir():
    import mawk
    init(dirs)
    cmd = "-", "-d", '-f\t'
    out = kept, transformed, reduced, formatted = mawk.main(cmd, mock_stdin)
    show(out)
    foo = {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert kept == foo
    assert transformed == foo
    assert reduced == foo
    assert formatted == '0 ~/Dropbox/scripts/cli\n1 ~/Dropbox/scripts\n2 ~'
    p('done')
    return 'pass'


def test_rp():
    import mawk  # TODO: remove?
    init(dirs)
    cmd = "-", "-d", '-f\t', '-rp', '"Dropbox" not in V'
    kept, transformed, reduced, formatted = out = mawk.main(cmd, mock_stdin)
    show(out)
    assert kept == {2: {0: '2', 1: '~'}}
    assert transformed == {2: {0: '2', 1: '~'}}
    assert reduced == {2: {0: '2', 1: '~'}}
    assert formatted == '2 ~'


def test_cmd():
    import mawk
    cmd = '{1:2}[1]', 'sum(range(100))', '-d'
    kept, transformed, reduced, formatted = out = mawk.main(cmd)
    show(out)
    assert formatted == [2, 4950]


def test_fp():
    import mawk
    init(dirs)
    cmd = "-", "-d", '-f\t', '-fp', '"Dropbox" not in V'
    kept, transformed, reduced, formatted = out = mawk.main(cmd, mock_stdin)
    show(out)
    assert kept == {0: {0: '0'}, 1: {0: '1'}, 2: {0: '2', 1: '~'}}
    assert transformed == {0: {0: '0'}, 1: {0: '1'}, 2: {0: '2', 1: '~'}}
    assert reduced == {0: {0: '0'}, 1: {0: '1'}, 2: {0: '2', 1: '~'}}
    assert formatted == '0\n1\n2 ~'


def test_ft():
    import mawk
    init(dirs)
    cmd = "-", "-d", '-f\t', '-ft', 'v*2'
    kept, transformed, reduced, formatted = out = mawk.main(cmd, mock_stdin)
    show(out)
    assert kept == {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert transformed == {0: {0: '00', 1: '~/Dropbox/scripts/cli~/Dropbox/scripts/cli'},
                           1: {0: '11', 1: '~/Dropbox/scripts~/Dropbox/scripts'}, 2: {0: '22', 1: '~~'}}
    assert reduced == {0: {0: '00', 1: '~/Dropbox/scripts/cli~/Dropbox/scripts/cli'},
                       1: {0: '11', 1: '~/Dropbox/scripts~/Dropbox/scripts'}, 2: {0: '22', 1: '~~'}}
    assert formatted == '00 ~/Dropbox/scripts/cli~/Dropbox/scripts/cli\n11 ~/Dropbox/scripts~/Dropbox/scripts\n22 ~~'


def init(test):
    global mock_stdin
    mock_stdin = MockStdin(test)


def show(out):
    kept, transformed, reduced, formatted = out
    p('show', 'kept', kept, 'transformed', transformed, 'reduced', reduced, 'formatted', formatted)


def write_asserts(out):
    kept, transformed, reduced, formatted = out
    for k, v in zip('kept transformed reduced formatted'.split(), out):
        print('\tassert %s == %s' % (k, repr(v)))


tests = [test_curry, test_dir, test_rp, test_cmd, test_fp, test_ft]
#tests = tests[-1:]
#tests = [test_rp]


def test():
    arguments.init('-d')
    for i, t in enumerate(tests):
        p(i)
        t()
        p('..............................')


if __name__ == '__main__':
    print('test.main')
    init()
    test()
    print('done')