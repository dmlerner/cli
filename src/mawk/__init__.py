#print('__init__')
import sys
import importlib
def reload():
#    print('reload')
    importlib.reload(formatter)
    importlib.reload(functionmaker)
    importlib.reload(logger)
    importlib.reload(mawk)
from . import arguments, formatter, functionmaker, logger, mawk, utils
#from .__main__ import main 
#print('leaving init')
