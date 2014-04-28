#!/usr/bin/env python
"""
This file does nothing except to open the file as specified on the command
line, reading it into a buffer and writing the same content back to the file.

This script is used to simulate the optimization of an image file without
actually doing it.
"""
import sys

if len(sys.argv) < 2:
    raise Exception('Missing filename')
with open(sys.argv[1], 'rb') as reader:
    buf = reader.read()
with open(sys.argv[1], 'wb') as writer:
    writer.write(buf)
