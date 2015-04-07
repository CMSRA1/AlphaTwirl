# Tai Sakuma <tai.sakuma@cern.ch>
import os
import pandas

##____________________________________________________________________________||
class TblNevt(object):
    def __init__(self, outPath):
        self._outPath = outPath
        self._tbl = pandas.DataFrame(columns = ('component', 'nevt'))

        self._getNEventsFor = getNEventsFor

    def begin(self): pass

    def read(self, component):
        nevt = self._getNEventsFor(component)
        self._tbl = self._tbl.append(pandas.DataFrame({'component': (component.name, ), 'nevt': (nevt, )}))

    def end(self):
        f = self._open(self._outPath)
        if len(self._tbl.index) == 0:
            f.write(" ".join([i for i in self._tbl.columns]) + "\n")
        else:
            self._tbl.nevt = self._tbl.nevt.apply(lambda x: '%.3f' % x)
            self._tbl.to_string(f, index = False)
            f.write('\n')
        self._close(f)

    def _open(self, path): return open(path, 'w')
    def _close(self, file): file.close()

##____________________________________________________________________________||
def getNEventsFor(component):
    file = open(os.path.join(component.skimAnalyzerCount.path, 'SkimReport.txt'))
    file.readline() # skip the 1st line
    lines = [l.strip() for l in file]
    lines = [l for l in lines if l.startswith('Sum Weights')]
    return float(lines[0][len('Sum Weights'):].strip().split()[0])

##____________________________________________________________________________||
