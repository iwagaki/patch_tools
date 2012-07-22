#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import subprocess

import processutil
import diffutil

def create_format_patch_without_header(sha1):
    lines = get_format_patch(sha1)
    patch = ''
    is_chunk_body = False

    for line in lines:
        m = re.match("^\-\-\- a", line);
        if m:
            is_chunk_body = False

        m = re.match("^\-\- $", line);
        if m:
            is_chunk_body = False

        if not is_chunk_body:
            patch += line + '\n'

        m = re.match("^\+\+\+ b/(.+)$", line);
        if m:
            is_chunk_body = True
            patch += get_git_diff_without_comment(sha1, m.group(1))

    return patch

def git_cherry_pick_without_header(sha1):
    patch = create_format_patch_without_header(sha1)
    if patch == '':
        return -1

    pid = str(os.getpid())
    fifo_patch = '/tmp/patch.' + pid

    try:
        _write_file(fifo_patch, patch.encode('utf-8'))
        result = processutil.run('git am ' + fifo_patch)
    finally:
        os.remove(fifo_patch)

    return result

def remove_comment(lines):
    body = []
    in_comment = False

    for line in lines:
        if line.find('<!--') == 0:
            in_comment = True

        if line.find('/*') >= 0:
            in_comment = True

        if in_comment:
            if line.find('-->') == 0 or line.find('*/') >= 0:
                in_comment = False
        else:
            if line.find('//') == 0:
                continue

            if line.find('#') == 0:
                continue

            body += line + '\n'

    return body

def get_git_diff_without_comment(sha1, path):
    previous = ''.join(remove_comment(get_file(sha1 + '^', path)))
    current = ''.join(remove_comment(get_file(sha1, path)))

    return diffutil.get_diff(previous, current, 'diff -u', '| tail -n +3')

def get_file(sha1, path):
    return processutil.get_output_lines('git show ' + sha1 + ':' + path + ' 2>/dev/null')

def get_format_patch(sha1):
    return processutil.get_output_lines('git format-patch --stdout ' + sha1 + '^..' + sha1)

def _write_file(path, src):
    f = open(path, 'w')
    try:
        f.write(src)
    finally:
        f.close()

if __name__ == '__main__':
    git_cherry_pick_without_header(sys.argv[1])
