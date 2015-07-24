#!/usr/bin/env python2

import sys
from os import unlink
from os.path import exists

HEADERS = ('Content-Disposition', 'Content-Length', 'Content-Type',
           'ETag', 'Last-Modified')

def is_sig_header(header):
    header = header.lower()
    for s in HEADERS:
        if header.startswith(s.lower()):
            return True

def do():
    headers_fn = sys.argv[1]
    signature_fn = sys.argv[2]

    # first, get all the headers from the latest request
    with open(headers_fn) as fd:
        headers = [line.strip() for line in fd.readlines()]

    last_index = 0
    for index, header in enumerate(headers):
        if header.startswith('HTTP/1.'):
            last_index = index
    headers = headers[last_index:]

    # select few headers for the signature
    headers = [header for header in headers if is_sig_header(header)]
    signature = '\n'.join(headers)

    # read the original signature
    if exists(signature_fn):
        with open(signature_fn) as fd:
            original_signature = fd.read()
        if original_signature == signature:
            return 0
        unlink(signature_fn)

    if signature:
        with open(signature_fn, 'w') as fd:
            fd.write(signature)

try:
    ret = do()
except:
    ret = 1

sys.exit(ret)

