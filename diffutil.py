#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import subprocess

def write_file(path, src):
    f = open(path, 'w')
    try:
        f.write(src)
    finally:
        f.close()

def get_diff_lines(src, dst):
    return get_diff(src, dst).splitlines()

def get_diff(src, dst):
    pid = str(os.getpid())
    fifo_src = '/tmp/src.' + pid
    fifo_dst = '/tmp/dst.' + pid
    os.mkfifo(fifo_src)
    os.mkfifo(fifo_dst)

    try:
        proc = subprocess.Popen('diff ' + fifo_src + ' ' + fifo_dst, shell = True, stdout = subprocess.PIPE)
        write_file(fifo_src, src.encode('utf-8'))
        write_file(fifo_dst, dst.encode('utf-8'))
        stdout = proc.communicate()[0].decode('utf-8')
    finally:
        os.unlink(fifo_src)
        os.unlink(fifo_dst)

    return stdout

if __name__ == '__main__':
    print get_diff('abc\n', 'def\n')
