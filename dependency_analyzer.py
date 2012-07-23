#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import re
import sys

import processutil

def main():
    argvs = sys.argv

    if (len(argvs) == 2):
        patch_list = argvs[1]
    else:
        patch_list = 'patch.csv'

    rows = list(csv.reader(file(patch_list, 'r')))
    total = len(rows)

    target_domains = list(csv.reader(file('domain.csv', 'r')))

    count = 0
    independent_count = 0
    dependent_count = 0

    domain_list = {}
    depth_map = {}

    for row in rows:
        sha1 = row[1]
        title = row[2]

        on_target_domains = False
        depth = 0
        print sha1

        lines = processutil.get_output_lines('git show ' + sha1)
        for line in lines:
            m = re.match("^\-\-\- a\/(.*)", line);
            if m:
                path = m.group(1)
                max_path = path
                print path

            m = re.match("@@ \-(\d+),(\d+) \+(\d+),(\d+) @@", line);
            if m:
                src_begin = int(m.group(1))
                src_end = int(m.group(2)) + src_begin - 1
                print src_begin, src_end

                blame_lines = processutil.get_output_lines('git blame -e -l -L ' + str(src_begin) + ',' + str(src_end) + ' ' + sha1 + '^ -- ' + path)

                for blame_line in blame_lines:
                    m = re.match("([\w\^]+) \(\<[\w\-_\.]+@([\w\-_\.]+)\>", blame_line);
                    if m:
                        base_sha1 = m.group(1)
                        domain = m.group(2)
                        if domain in target_domains:
                            on_target_domains = True
                            if depth_map.has_key(base_sha1):
                                if depth < depth_map[base_sha1][0] + 1:
                                    depth = depth_map[base_sha1][0] + 1
                                    max_path = path
                                    print 'base_sha1 = ' + base_sha1 + ', depth = ' + str(depth)
                            else:
                                print 'Error: cannot find base_sha1 ' + base_sha1

                        domain_list[domain] = 1

        depth_map[sha1] = [depth, max_path]
        if on_target_domains:
            dependent_count += 1
        else:
            independent_count += 1

        print sha1 + ': depth = '+ str(depth) + ', path = ' + path + ', size = ' + str(len(depth_map))
        count += 1

        print '[' + str(count) + '/' + str(total) + '] independent: ' + str(independent_count) + ' dependent: ' + str(dependent_count)

    print domain_list

    f = open('result.csv', 'w')
    for k, v in sorted(depth_map.items(), key=lambda x:x[1][0]):
        print k + ',' + str(v[0]) + ',' + v[1]
    f.close()

if __name__ == '__main__':
    main()
