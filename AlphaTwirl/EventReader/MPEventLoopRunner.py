# Tai Sakuma <tai.sakuma@cern.ch>

##__________________________________________________________________||
class MPEventLoopRunner(object):
    def __init__(self, communicationChannel):
        self.communicationChannel = communicationChannel
        self._ntasks = 0

    def begin(self):
        self._allReaders = { }
        self._progressMonitor = self.communicationChannel.progressMonitor
        self.task_queue = self.communicationChannel.task_queue
        self.result_queue = self.communicationChannel.result_queue

    def run(self, eventLoop):

        # add id so can collect later
        reader = eventLoop.reader
        reader.id = id(reader)
        self._allReaders[id(reader)] = reader

        self.task_queue.put(eventLoop)
        self._ntasks += 1

    def end(self):

        while self._ntasks >= 1:
            self._progressMonitor.monitor()
            if self.collectTaskResults():
                self._ntasks -= 1

        self._progressMonitor.last()

    def collectTaskResults(self):
        if self.result_queue.empty(): return False
        reader = self.result_queue.get()
        self._allReaders[reader.id].setResults(reader.results())
        return True

##__________________________________________________________________||
