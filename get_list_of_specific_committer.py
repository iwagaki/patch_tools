#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from processutil import ProcessUtil

def main():
    committer = sys.argv[1]
    ProcessUtil.run('git log --topo-order --reverse --no-merges --committer=\'%s\' --format=\'\"\%%ci\",%%H,\"%%s\"\'' % committer)

if __name__ == '__main__':
    main()
