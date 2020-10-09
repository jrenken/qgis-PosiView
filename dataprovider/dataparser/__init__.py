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

PARSERS = ('IX_USBL', 'PISE', 'MINIPOS', 'GPS', 'RANGER2', 'CP16', 'COMPASS', 'AIS', 'MARUM', 'TARGET_POS')


def createParser(parserType=''):
    if parserType.upper() == 'IX_USBL':
        from .parser_ixusbl import IxUsblParser
        return IxUsblParser()
    if parserType.upper() == 'PISE':
        from .parser_pise import PiseParser
        return PiseParser()
    if parserType.upper() == 'MINIPOS':
        from .parser_minipos import MiniPosParser
        return MiniPosParser()
    if parserType.upper() == 'GPS':
        from .parser_gps import GpsParser
        return GpsParser()
    if parserType.upper() == 'RANGER2':
        from .parser_ranger2 import Ranger2Parser
        return Ranger2Parser()
    if parserType.upper() == 'CP16':
        from .parser_cp16 import CP16Parser
        return CP16Parser()
    if parserType.upper() == 'COMPASS':
        from .parser_compass import CompassParser
        return CompassParser()
    if parserType.upper() == 'AIS':
        from .parser_ais import AisParser
        return AisParser()
    if parserType.upper() == 'MARUM':
        from .parser_pmtm import PmtmParser
        return PmtmParser()
    if parserType.upper() == 'TARGET_POS':
        from .parser_targetpos import TargetPosParser
        return TargetPosParser()

    from .parser import Parser
    return Parser()
