#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import subprocess
import time

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

def get_author_email(sha1):
    return processutil.get_output_lines('git log -1 --pretty="%ae" ' + sha1)[0]

def get_author_date(sha1):
    return processutil.get_output_lines('git log -1 --pretty="%ai" ' + sha1)[0]

def get_committer_email(sha1):
    return processutil.get_output_lines('git log -1 --pretty="%ce" ' + sha1)[0]

def get_committer_date(sha1):
    return processutil.get_output_lines('git log -1 --pretty="%ci" ' + sha1)[0]

def get_committer_domain(sha1):
    email = processutil.get_output_lines('git log -1 --pretty="%ce" ' + sha1)[0]
    m = re.match("[\w\-_\.]+@([\w\-_\.]+)", email)
    if not m:
        print 'Error: cannot find a domain: ' + email
        cleanup_and_abort()

    return m.group(1)

def get_committer_year(sha1):
    unix_time = int(processutil.get_output_lines('git log -1 --pretty="%ct" ' + sha1)[0])
    return time.gmtime(unix_time).tm_year

def get_cherrypick_origin(sha1):
    lines = processutil.get_output_lines('git log -1 ' + sha1)

    origin_list = []

    for line in lines:
        m = re.match("\s*\(cherry(?:\s+)?(?:-)?pick(?:ed)?\s+from:?(?:\s+commit)?:?\s+([0-9a-f]+)\s*\)", line, re.IGNORECASE);
        if m:
            origin_list.append(m.group(1))

    return origin_list

def _write_file(path, src):
    f = open(path, 'w')
    try:
        f.write(src)
    finally:
        f.close()

if __name__ == '__main__':
    git_cherry_pick_without_header(sys.argv[1])
