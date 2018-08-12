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
        print('Starting runnable.')
        self._running = True
        self._loop.start()
    
    def stop(self):
        """ Stop the Runnable's main _loop. """
        self._running = False
        self._loop.join()
    
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
    
    @property
    def running(self) -> bool:
        """ Get whether this runnable is running """
        return self._running
    
    @property
    def queue(self) -> Mp.Queue:
        return self._queue