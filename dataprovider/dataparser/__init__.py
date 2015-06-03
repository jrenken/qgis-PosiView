import os, glob
import sys

sys.path.append(os.path.realpath(os.path.dirname(os.path.abspath(__file__))))
parsers = [ os.path.splitext(os.path.basename(f))[0] 
           for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parser_*.py'))] 



def createParser(parserType = ''):
    for prs in parsers:
        p = __import__(prs)
        print dir(p)
        if parserType.upper() == p.__id__:
            return p.__parser__()
        
    raise Exception('Could not create parser for ', parserType)

