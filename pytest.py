import sys
import time

import subprocess
import argparse
import time

def t(*x):
    print('('+str(round(time.time() % 1000, 3)) + '\n' + '\n'.join(map(str, x)) + '\n\n'+')')

lines = []
for line in sys.stdin:
    lines.append(line.strip())
    #sys.stderr.write('line')
    #sys.stderr.write(line)
stdin = '\n'.join(lines)
#sys.stderr.write('lines joined')
#sys.stderr.write(stdin)

parser = argparse.ArgumentParser()
parser.add_argument('-n', default='nothing', nargs='?')
#print('%s: you said %s' % (sys.argv[0], '\n'.join(sys.argv[1:])))
t('X %s ' % sys.argv[1] + ' ' + stdin)
'''
args = parser.parse_args()
cmd = "awk 'BEGIN{FS=\"%s\"; RS=\"%s\"} {print $%s}'" % tuple(map(str, (args.f, args.r, args.n)))
#print(cmd)
proc = subprocess.Popen(['/bin/zsh', '-i', '-c', cmd], stdout=subprocess.PIPE)
stdout, stderr = [x and x.decode() for x in proc.communicate()]
print(stdout)
#print(stdout, stderr)
#time.sleep(3)
#print('asdf')
#print('Done')
'''
