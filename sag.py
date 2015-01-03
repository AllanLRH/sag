#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import division
from __future__ import print_function

from collections import defaultdict
import subprocess
from colorama import Fore, Back, Style, init
init()
import re
import sys
# import ipdb

printName = lambda filename: print('\n' + Fore.CYAN + filename + ' ' + Fore.RESET)
split = re.compile('[:; ]').split

def parseAckMateData(agResult):
    lines = agResult.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    matchDict = defaultdict(list)
    for line in lines:
        if line.startswith(':'):
            name = line[1:]
        else:
            linenumber, beginindex, endindex, matchline = split(line, maxsplit=3)
            matchDict[name].append((linenumber, int(beginindex), int(endindex), matchline))
    return matchDict


def printMatchDict(matchDict):
    for filename in matchDict:
        printName(filename)
        for match in matchDict[filename]:
            linenumber, beginindex, endindex, matchline = match
            afterindex = beginindex + endindex
            beforeHightlight = matchline[0:beginindex]
            highlighted      = Fore.YELLOW + matchline[beginindex:afterindex] + Fore.RESET
            afterHighlight   = matchline[afterindex:]
            print(Fore.RED + linenumber.rjust(4) + ': ' + Fore.RESET + beforeHightlight + highlighted + afterHighlight)


def callAg():
    command = ['/usr/local/bin/ag', '--ackmate'] + sys.argv[1:]
    call = subprocess.Popen(command, stdout=subprocess.PIPE)
    try:
        result = call.communicate()[0]
        result = result.decode('utf8')
        return result
    except Exception, e:
        print('Communication with ag failed\n\n')
        raise e


def openInSublimeText(filename, linenumber=None, columnnumber=None):
    # subl file:line:column
    if linenumber is not None:
        filename += ':{}'.format(linenumber)
        if columnnumber is not None:
            filename += ':{}'.format(columnnumber)
    subprocess.Popen(['subl', filename])


if __name__ == '__main__':
    agResult = callAg()
    matchDict = parseAckMateData(agResult)
    printMatchDict(matchDict)
