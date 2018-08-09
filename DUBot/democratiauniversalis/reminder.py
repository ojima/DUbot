from democratiauniversalis.runnable import Runnable

class Reminder(Runnable):
    def __init__(self):
        super().__init__()
        self.delta = 0.5
    
    def update(self):
        pass