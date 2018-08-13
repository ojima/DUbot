import datetime
import time

import multiprocessing as Mp


class Runnable:
    """
        A basic (abstract) class for runnables to be instantized by the client.
        @author ojima
    """
    def __init__(self):
        self._running = False
        self._loop = Mp.Process(target = self.run)
        self._delta = 1.0
        self._queue = Mp.Queue()
    
    def start(self):
        """ Start the Runnable's main _loop. """
        self._running = True
        self._loop.start()
        self.log('Starting {0}.'.format(self.name))
    
    def stop(self):
        """ Stop the Runnable's main _loop. """
        self.log('Stopping {0}.'.format(self.name))
        self._running = False
        self._loop.terminate()
    
    def run(self):
        last = time.time()
        
        while self._running:
            now = time.time()
            if now - last > self._delta:
                last = now
                self.update()
            else:
                time.sleep(self._delta / 100.0)
    
    def update(self):
        """ Abstract method for runnable update execution. """
        pass
    
    def log(self, msg):
        print('[{0}] {1}-{2}: {3}'.format(datetime.datetime.now().strftime('%H:%M:%S'), self.name, self._loop.pid, msg))
    
    @property
    def running(self) -> bool:
        """ Get whether this runnable is running """
        return self._running
    
    @property
    def queue(self) -> Mp.Queue:
        return self._queue
    
    @property
    def name(self):
        return 'runnable'

class Saveable:
    """ A saveable is any class that has a load and a save method """
    def save(self, filename):
        pass
    
    def load(self, filename):
        pass