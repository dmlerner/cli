import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', default='\\t', nargs='?')
parser.add_argument('-r', default='\\n', nargs='?')
parser.add_argument('-n', default=1, type=int, nargs='?')
args = parser.parse_args()
print(args)
# precommand = 'dirs'
# precommand = "echo 'aqbpcqdpeqf'"
precommand = "echo 'a,b;c,d;e,f'"
cmd = "%s | awk 'BEGIN{FS=\"%s\"; RS=\"%s\"} {print $%s}'" % tuple(map(str, (precommand, args.f, args.r, args.n)))
# cmd = "%s | awk 'BEGIN{RS='%s'} {print $%s}'" % tuple(map(str, (precommand, args.r, args.n)))
print(cmd)
output = subprocess.check_output(['/bin/zsh', '-i', '-c', cmd]).decode()
print(output)
