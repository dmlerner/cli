print('__main__')
from . import arguments
from . import mawk


# Fix for broken pipe error I don't quite understand
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

if __name__ == '__main__':
    arguments.init() # TODO: reload? combine reload with init? 
    kept, transformed, reduced, formatted = mawk.main()
