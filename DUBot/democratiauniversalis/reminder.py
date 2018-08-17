import datetime
import json

from democratiauniversalis.prototypes import Runnable, Saveable

class Reminder(Runnable, Saveable):

    def __init__(self, game, queue, filename = None):
        super().__init__()
        self._delta = 0.5
        self._game = game
        self._outqueue = queue
        self._filename = filename

        self._reminders = { }
        self._remind_id = 0

    def update(self):
        # Polling for events.
        while not self.queue.empty():
            event = self.queue.get()

            if event['type'] == 'remind':
                who = event['target']
                when = event['time']
                why = event['details']

                self._reminders[self._remind_id] = { 'who' : who, 'when' : when, 'why' : why, 'type' : 'generic' }
                self._remind_id += 1

                self.save(self._filename)
            elif event['type'] == 'vote':
                # Create reminders for votes.
                when = event['time'] + datetime.timedelta(hours = 12)
                when.minute = 0
                when.second = 0
                when.microsecond = 0

                reminder = 'Dear {0},\nPlease remember to vote on the **{1}**!\nLink: {2}'

                for player in self._game.players:
                    if player.get_setting('remind-me'):
                        self.queue.put({ 'type' : 'remind', 'target' : player.uid, 'time' : when, 'why' : reminder.format(player.username, event['title'], event['url']), 'type' : 'vote' })
            elif event['type'] == 'didvote':
                # A certain player voted, so we can delete their reminder
                for remind in self._reminders:
                    if self._reminders[remind]['type'] == 'vote' and self._reminders[remind]['target'] == event['target']:
                        del self._reminders[remind]

        # Polling for reminders
        now = datetime.datetime.now()
        for remind in self._reminders:
            when = self._reminders[remind]['when']

            if when >= now:
                self._outqueue.put({ 'to' : self._reminders[remind]['who'], 'message' : self._reminders[remind]['why'] })

    def load(self, filename):
        with open(filename, 'r') as fp:
            dct = json.load(fp)

        self._remind_id = dct['total-reminders']
        self._reminders = dct['active-reminders']

    def save(self, filename):
        dct = { 'total-reminders' : self._remind_id, 'active-reminders' : self._reminders }

        with open(filename, 'w') as fp:
            json.dump(dct, fp, indent = 2)

    @property
    def name(self):
        return 'reminder-manager'