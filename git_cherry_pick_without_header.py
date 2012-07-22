#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys

import processutil
import gitutil

#is_retry_on = False
is_retry_on = True

def main():
    argvs = sys.argv

    if (len(argvs) == 2):
        patch_list = argvs[1]
    else:
        patch_list = 'patch.csv'

    rows = list(csv.reader(file(patch_list, 'r')))
    total = len(rows)
    count = 0
    success = 0
    success_wo_header = 0
    fail = 0
    error = 0

    for row in rows:
        sha1 = row[1]
        title = row[2]

        result = processutil.run('git cherry-pick ' + sha1)
        if result == 0:
            status = 'OK'
            success += 1
        else:
            processutil.run('git cherry-pick --abort')

            if is_retry_on:
                result = gitutil.git_cherry_pick_without_header(sha1)
                if result == 0:
                    status = 'OK'
                    success_wo_header += 1
                elif result == -1:
                    processutil.run('git am --abort')
                    status = 'ERR'
                    error += 1
                else:
                    processutil.run('git am --abort')
                    status = 'NG'
                    fail += 1
            else:
                status = 'NG'
                fail += 1

        count += 1
        print '[' + status + '] [' + str(count) + '/' + str(total) + '] [Succeed:' + str(success) + ' Success(w/o header):' + str(success_wo_header) + ' Failed:' + str(fail) + ' Error:' + str(error) + '] ' + sha1 + ': ' + title

if __name__ == '__main__':
    main()
