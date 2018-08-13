import queue

from democratiauniversalis.prototypes import Runnable

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
                
                if event['type'] == 'give':
                    pass
                
        except queue.Empty:
            return
    
    @property
    def name(self):
        return 'role-manager'