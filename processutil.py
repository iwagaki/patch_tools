#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import traceback

class ProcessUtil:
    @staticmethod
    def get_output(cmd):
        proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
        stdout = proc.communicate()[0].decode('utf-8')
        if not proc.returncode == 0:
            print 'Waring: return code = ' + str(proc.returncode)
            traceback.print_stack()
        return stdout

    @staticmethod
    def get_output_lines(cmd):
        return get_output(cmd).splitlines()

    @staticmethod
    def run(cmd, output_file = None):
        args = { 'shell': True }
        if output_file:
            args['stdout'] = output_file
        return subprocess.call(cmd, **args)

if __name__ == "__main__":
    print ProcessUtil.get_output(' '.join(sys.argv[1:]))
