#!/usr/bin/python3

from utils import curry, vector, map, equal
from logger import p
import mawk

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
        self.x = x

    def read(self):
        return self.x

    def __iter__(self):
        return iter(self.x)


def add(x):
    return x + 1


def test_curry():
    global args
    import arguments
    arguments.init()
    from arguments import args
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
    import driver
    cmd = "-", "-test=%s" % dirs, "-d", '-f\t'
    kept, transformed, reduced, formatted = driver.main(cmd)
    foo = {0: {0: '0', 1: '~/Dropbox/scripts/cli'}, 1: {0: '1', 1: '~/Dropbox/scripts'}, 2: {0: '2', 1: '~'}}
    assert kept == foo
    assert transformed == foo
    assert reduced == foo
    assert formatted == '0 ~/Dropbox/scripts/cli\n1 ~/Dropbox/scripts\n2 ~'
    p('done')
    return 'pass'


def init():
    global args, mock_stdin
    from arguments import args
    mock_stdin = MockStdin(args.test)


tests = [test_curry, test_dir]


def test():
    for i, t in enumerate(tests):
        print(i)
        print(t())


if __name__ == '__main__':
    test()
