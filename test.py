#!/usr/bin/env python2
import string

import commands
import re
import sys
import versioning_library

versioning_library.update_tag('default.xml','tf-module-vpc','123','output.xml')
# for line in open('default.xml','r'):
#   output_line = line
#   if re.match(r'.*?project name="tf-module-vpc".*?', output_line):
#     output_line=commands.getstatusoutput('echo \''+output_line+'\' | sed  \'s/revision=\\"[^"]*\\"/revision=\\"123\\"/\'')[1]
#   sys.stdout.write(output_line)
