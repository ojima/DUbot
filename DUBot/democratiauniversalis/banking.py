import multiprocessing as Mp

from democratiauniversalis.runnable import Runnable

class Banking(Runnable):

    def __init__(self, queue):
        super().__init__()

        self._lock = Mp.Lock()
        self._outqueue = queue

    def update(self):
        pass