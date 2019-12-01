#!/usr/bin/python3

from mawk import curry, vector, map, p


def add(x):
    return x + 1


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
    print(a, b, c)


g(1)(2)


# Test data
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
