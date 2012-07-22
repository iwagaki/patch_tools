#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

dir_list = []

def pushd(path):
    dir_list.append(os.getcwd())
    os.chdir(path)

def popd():
    os.chdir(dir_list.pop())

if __name__ == '__main__':
    pushd('/')
    print os.getcwd()
    popd()
    print os.getcwd()
