import subprocess
import argparse
import time
import sys


def t(*x):
    sys.stderr.write(str(round(time.time() % 1000, 3)) + '\n' + '\n'.join(map(str, x)) + '\n\n')


t('reading sys.stdin')
lines = []
for line in sys.stdin:
    #from_stdin = sys.stdin.read()
    lines.append(line.strip())
    t('stdin lin', line)
t('lines', lines)
from_stdin = '\n'.join(lines)
t('from_stdin', from_stdin)
time.sleep(.5)
t('slept')

parser = argparse.ArgumentParser()
parser.add_argument('-f', default='\\t', nargs='?')
parser.add_argument('-r', default='\\n', nargs='?')
parser.add_argument('-n', default=1, type=int, nargs='?')
t('parsing args')
args = parser.parse_args()
t(args)

cmd = "awk 'BEGIN{FS=\"%s\"; RS=\"%s\"} {print $%s}'" % tuple(map(str, (args.f, args.r, args.n)))
t('cmd=', cmd)
# print(cmd)
proc = subprocess.Popen(['/bin/zsh', '-i', '-c', cmd],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        # shell=True,
                        encoding='utf8'
                        )
t('made proc')
proc.stdin.write(from_stdin)
t('wrote')
stdout = proc.stdout.read()
t('read', stdout)
#stdout, stderr = proc.communicate(from_stdin)
#t('communicated', stdout, stderr, '/communicated')
#print('??' + stdout + '\nlinetwo')
print(from_stdin)
t('stdouted but secretly its just the input i had on purpose...')
time.sleep(3)
t('slept, done')
