import queue

from democratiauniversalis.runnable import Runnable

class RoleManager(Runnable):
    def __init__(self, game, queue):
        super().__init__()
        self._delta = 0.5
        self._game = game
        self._outqueue = queue
    
    def update(self):
        # Polling for events.
        try:
            while True:
                event = self.queue.get()
                # Do stuff with event
        except queue.Empty:
            return