import time
import multiprocessing as Mp

class Runnable:
    """
        A basic (abstract) class for runnables to be instantized by the client.
        @author ojima
    """
    def __init__(self):
        self.running = False
        self.loop = Mp.Process(target = self.run)
        self.delta = 1.0
    
    def start(self):
        """ Start the Runnable's main loop. """
        print('Starting runnable.')
        self.running = True
        self.loop.start()
    
    def stop(self):
        """ Stop the Runnable's main loop. """
        self.running = False
        self.loop.join()
    
    def run(self):
        last = time.time()
        
        while self.running:
            now = time.time()
            if now - last > self.delta:
                last = now
                self.update()
            else:
                time.sleep(self.delta / 100.0)
    
    def update(self):
        pass