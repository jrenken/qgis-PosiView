'''
Created on 30.06.2023

@author: Torsten Pfuetzenreuter
'''
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import map
from builtins import range
from builtins import object

from datetime import datetime, timezone
import re
from .parser import Parser

# import QgsMessageLog to log error messages
try:
    from qgis.core import QgsMessageLog, Qgis
    log_error = True
except ImportError:
    log_error = False

name_mapping = {
    'name': ('id', str),
    'time': ('time', float),
    'lat': ('lat', float),
    'lon': ('lon', float),
    'dep': ('depth', float),
    'hdg': ('heading', float),
    'spd': ('velforw', float),
    'mode': ('text', lambda x: x.split('@')[1]),
}


def split_node_report(nr: str) -> list:
    """
    Splits a node report into strings of the form KEY=VALUE
    Note: VALUE may contain the KEY separator (comma)
    """
    pattern = r'(\w+)='
    indices = [m.start() for m in re.finditer(pattern, nr)]
    indices.append(None)
    parts = [nr[indices[i]:indices[i + 1]] for i in range(len(indices) - 1)]
    # remove trailing comma
    for i, s in enumerate(parts):
        if s.endswith(','):
            parts[i] = s[:-1]
    return parts


class MoosNodeReportParser(Parser):
    """
    Parser for MOOS NODE_REPORT text messages
    e.g. NAME=uuv1,TYPE=UUV,TIME=1252348077.59,X=51.71,Y=-35.50,LAT=43.824981,LON=-70.329755,SPD=2.00,HDG=118.85,YAW=118.84754,DEP=4.63,LENGTH=3.8,MODE=MODE@ACTIVE:LOITERING
    """
    def parse(self, data):
        result = {}
        # split string by separator (,)
        # easy way would be to use data.split(','), but this fails when the reports contains further comma
        # (see ALLSTOP=... in the test example at file end)
        # for var in data.strip().split(','):
        for var in split_node_report(data.strip()):
            try:
                name, value = var.split('=')
                name = name.lower()
                if name in name_mapping:
                    result[name_mapping[name][0]] = name_mapping[name][1](value)
                else:
                    pass
            except Exception:
                if log_error:
                    QgsMessageLog.logMessage(f"Unable to parse '{var}' from NODE_REPORT '{data}'", tag="PosiView", level=Qgis.Critical)
                else:
                    raise
        return result


if __name__ == "__main__":
    p = MoosNodeReportParser()
    print(p.parse('NAME=uuv1,X=-33.54,Y=-75.33,SPD=1.62,HDG=289.55,DEP=3.02,LAT=54.32936293,LON=10.15024244,TYPE=UUV,COLOR=red,MODE=MODE@MISSION:SURVEYING,ALLSTOP=MissingDecVars:speed,course,ALTITUDE=6.53,INDEX=3686,YAW=2.8002935,TIME=1252348077.33,LENGTH=2.5 '))
