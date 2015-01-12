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
reload(sys)
sys.setdefaultencoding("utf-8")
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


# Function tp print filenames. inArg: (index, filename)
printName = lambda inArg: print('\n' + Back.CYAN + Fore.BLACK + str(inArg[0]+1) + Fore.RESET + Back.RESET + ':   ' + Fore.CYAN + inArg[1] + ' ' + Fore.RESET)
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
    for idx, filename in enumerate(matchDict):
        printName((idx, filename))
        for idx, match in enumerate(matchDict[filename]):
            linenumber, beginindex, endindex, matchline = match
            afterindex = beginindex + endindex
            beforeHightlight = matchline[0:beginindex]
            highlighted      = Fore.YELLOW + matchline[beginindex:afterindex] + Fore.RESET
            afterHighlight   = matchline[afterindex:]
            print(Fore.CYAN + str(idx+1) + Fore.RESET + Fore.RED + linenumber.rjust(4) + ': ' + Fore.RESET + beforeHightlight + highlighted + afterHighlight)


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


def openInSublimeText(filesToOpen):
    """
    Function: openInSublimeText
    Open specified file in Sublime Text, optionally on a specified line and column.
    Assumes that Sublime Text is callable with 'subl'.
    Parameters:
      filesToOpen:    A list containing list with elements:
          filename:       File to open in Sublime Text (string)
          linenumber:     Linenumber to place caret at (int, optional)
          columnnumber:   ColumnNumber to put caret at (int, optional)
      as the one created from
    """
    # format for opening files in Sublime Text is:
    # subl file1 file2:line file3:line:column
    fileOpenSpecList = list()
    for toOpen in filesToOpen:
        fileOpenSpec = toOpen[0]
        if len(toOpen) > 1:
            fileOpenSpec += ':{}'.format(toOpen[1])
            if len(toOpen) > 2:
                fileOpenSpec += ':{}'.format(toOpen[2])
        fileOpenSpecList.append(fileOpenSpec)
    subprocess.Popen(['subl'] + fileOpenSpecList)


def promptUser(isFirstCall=True):
    """
    Function: promptUser
    Prompt the user for input.
    Can be terminated by pressing 'q'.
    If a blank line is entered, the promptUser will call itself recursively, but with
    the parameter isFirstCall = False, and thus terminate the program if a blank line
    is entered a second time.

    The input format is simple - example:
      1,2 4,3 6
    opens matched file number 1, with the cursor placed in the 2nd listed matched line,
    matched file number 4 with ther cursor placed on the 3rd matched line, and the 6th
    matched file.
    Parameters:
      isFirstCall - True if first call(default), should be False otherwise
    Returns:
      From the example above:
      [['1', '2'], ['4', '3'], ['6']]
    """
    promptCharacter = u' \u27A2  '  # Unicode symbol:  ➢
    initialPrompt   = u'\nEnter file numbers seperated by spaces, comma seperation for choosing line\n'
    if isFirstCall:
        userInput = raw_input(initialPrompt + promptCharacter).strip()
    else:
        userInput = raw_input(promptCharacter).strip()
    if not userInput.strip() and isFirstCall:
        promptUser(isFirstCall=False)
    elif not userInput.strip() and not isFirstCall:
        sys.exit()
    splitInput = userInput.split(' ')
    parsedInput = [el.split(',') for el in splitInput]
    return parsedInput


def executeUserPrompt(matchDict, parsedInput):
    """
    Function: executeUserPrompt
    Converts user input (file number and possoble a number indicating
    which of the matched lines the cursor should be positioned at) to
    the corresponding filepath, linenumber and columnnumber.
    It calls openInSublimeText to open the files specified by the user.
    Parameters:
      matchDict: Dict with matches from parseAckMateData
      parsedInput - The parsed input from promptUser
    """
    filenames = matchDict.keys()
    filesToOpen = list()
    for userInput in parsedInput:
        filename          = filenames[int(userInput[0]) - 1]
        matchedLineNumber = int(userInput[1]) - 1 if len(userInput) > 1 else None
        openArgs          = [filename]
        if matchedLineNumber:
            openArgs.append(matchDict[filename][matchedLineNumber][0])  # line number to place caret at
            openArgs.append(matchDict[filename][matchedLineNumber][1] + 1)  # Column number to place caret at, compensate for 0 indexing
        filesToOpen.append(openArgs)
    openInSublimeText(filesToOpen)


def main():
    """
    Function: main
    Calls all other functions in the script in the correct order,
    and passes data between them
    """
    agResult = callAg()
    matchDict = parseAckMateData(agResult)
    printMatchDict(matchDict)
    psersedUserInput = promptUser()
    executeUserPrompt(matchDict, psersedUserInput)


if __name__ == '__main__':
    main()
