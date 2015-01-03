#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import division
from __future__ import print_function

import py.test
import sag

with open("test/agAckMateUtf8.txt") as fid:
    agAckMateUtf8 = fid.read().decode('utf8')

with open("test/exampleTextNormalPipe.txt") as fid:
    exampleTextNormalPipe = fid.read()

with open("test/exampleTextNormalPipeLongLines.txt") as fid:
    exampleTextNormalPipeLongLines = fid.read()

