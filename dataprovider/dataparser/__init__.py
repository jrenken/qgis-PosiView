# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2015 Jens Renken (renken@marum.de)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################

# import os, glob
# import sys



# sys.path.append(os.path.realpath(os.path.dirname(os.path.abspath(__file__))))
# parsers = [ os.path.splitext(os.path.basename(f))[0] 
#            for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parser_*.py'))] 



def createParser(parserType = ''):
    if parserType.upper() == 'IX_USBL':
        from .parser_ixusbl import IxUsblParser
        return IxUsblParser()
    if parserType.upper() == 'PISE':
        from .parser_pise import PiseParser
        return PiseParser()
    
#     for prs in parsers:
#         p = __import__(prs)
#         print dir(p)
#         if parserType.upper() == p.__id__:
#             return p.__parser__()
#         
    raise Exception('Could not create parser for ', parserType)

