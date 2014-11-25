#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import division
from __future__ import print_function

from collections import defaultdict
import subprocess
import re

def parseNormalPipeData(lines):
    matchDict = defaultdict(list)
    spl = re.compile(':')
    for line in lines:
        filename, linenumber, matchstring = spl.split(line, maxsplit=2)
        matchDict[filename].append((linenumber.strip(), matchstring[0:-1]))  # matchstring[0:-1] strips newline
    return matchDict

def printMatchDict(matchDict):
    for filename in matchDict:
        print('\n' + filename)
        for match in matchDict[filename]:
            print(match[0].rjust(6) + ':  ' + match[1])
            # print(match[0] + ':  ' + match[1])


def testWithFileData(filePath):
    with open(filePath) as fid:
        data = fid.readlines()
    matches = parseNormalPipeData(data)
    printMatchDict(matches)

if __name__ == '__main__':
    testWithFileData("exampleTextNormalPipeLongLines.txt")
