#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import processutil

def main():
    committer = sys.argv[1]
    processutil.run('git log --topo-order --reverse --no-merges --committer=\'%s\' --format=\'\"%%ci\",%%H,\"%%s\"\'' % committer)

if __name__ == '__main__':
    main()
