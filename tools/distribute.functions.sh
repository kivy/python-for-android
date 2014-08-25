function npath
{
    python -c 'import os, sys;\
               x = os.path.join(*sys.argv[1:]);\
               x = os.path.expanduser(x);\
               x = os.path.realpath(x);\
               x = os.path.normpath(x);\
               x = os.path.abspath(x);\
               print(x)' "$@" 
}

