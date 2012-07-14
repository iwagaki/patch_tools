#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class DirUtil:
    dir_list = []

    @staticmethod
    def pushd(path):
        DirUtil.dir_list.append(os.getcwd())
        os.chdir(path)

    @staticmethod
    def popd():
        os.chdir(DirUtil.dir_list.pop())

if __name__ == '__main__':
    DirUtil.pushd('/')
    print os.getcwd()
    DirUtil.popd()
    print os.getcwd()
