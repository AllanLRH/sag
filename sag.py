#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import division
from __future__ import print_function

from collections import OrderedDict, Callable
import subprocess
from colorama import Fore, Back, Style, init
init()  # Initialize colorama
import re
import sys
# import ipdb


class DefaultOrderedDict(OrderedDict):
    """
    Class: DefaultOrderedDict
    An ordered dictionary with the default property of defaultdict.
    For additional magic methods used for copying and pickeling, see
    http://stackoverflow.com/questions/6190331/
    Extends: OrderedDict
    """
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
           not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory, OrderedDict.__repr__(self))


printName = lambda filename: print('\n' + Fore.CYAN + filename + ' ' + Fore.RESET)  # Function tp print filenames
split = re.compile('[:; ]').split  # function to split the lines from ackmate

def parseAckMateData(agResult):
    """
    Function: parseAckMateData
    Parses result from 'ag --ackmate'
    Parameters:
      agResult: Result from 'ag --ackmate' (multiline string)
    Returns:
      Dictionary where the keys are filenames and the contents is a list of tuples.
      The list contains all the tuples, which contains the matches in the format:
        (linenumber, beginindex, endindex, matchline)
      Where the variables are as follows:
        linenumber: The line number of the match (string)
        beginindex: The column number where the matched word begins (int)
        endindex:   The column number where the matched word ends (int)
        matchline:  The line contens where the match occured (string)
    """
    lines = agResult.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    matchDict = DefaultOrderedDict(list)
    for line in lines:
        if line.startswith(':'):
            name = line[1:]
        else:
            linenumber, beginindex, endindex, matchline = split(line, maxsplit=3)
            matchDict[name].append((linenumber, int(beginindex), int(endindex), matchline))
    return matchDict


def printMatchDict(matchDict):
    """
    Function: printMatchDict
    Prints out the matched dict nicely formattet.
    Parameters:
      matchDict: Dict with matches from parseAckMateData
    """
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
    """
    Function: callAg
    Calls ag. Everything after 'sag' is passed to the search
    Returns:
      Multiline string with ag result.
    """
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
    """
    Function: openInSublimeText
    Open specified file in Sublime Text, optionally on a specified line and column.
    Assumes that Sublime Text is callable with 'subl'.
    Parameters:
      filename:       File to open in Sublime Text (string)
      linenumber:     Linenumber to place caret at (int, optional)
      columnnumber:   ColumnNumber to put caret at (int, optional)
    """
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
