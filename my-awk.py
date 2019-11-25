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
#time.sleep(.5)
#t('slept')

parser = argparse.ArgumentParser()
parser.add_argument('-n', default=1, type=int, nargs='?')
args = parser.parse_args()
t(args)

cmd = 'cut -c 2-'
t('cmd=', cmd)
# print(cmd)
proc = subprocess.Popen(['/bin/zsh', '-i', '-c', cmd],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=sys.stderr,
                        close_fds=True,
                        universal_newlines=True,
                        # shell=True,
                        encoding='utf8'
                        )
t('made proc')
to_send = from_stdin * args.n
#print(to_send)
stdout, stderr = proc.communicate(to_send)
proc.kill()
#stdout, stderr = proc.communicate()

t('communicated', 'XXX'+stdout, stderr, '/communicated')
print(stdout)
t('printed to my stdout')
time.sleep(2)
t('slept, done')
