import json

from democratiauniversalis.metagame.player import Player

class Game:
    """ The main game handler. """
    def __init__(self):
        self._players = { }
        self._owners = [ ]
    
    def load(self, filename):
        with open(filename, 'r') as rfile:
            dct = json.load(rfile)
        
        for uid in dct['players']:
            player = Player(self, uid)
            player.from_dict(dct['players'][uid])
            self._players[uid] = player
    
    def save(self, filename):
        dct = { }
        dct['players'] = { }
        
        for player in self._players:
            dct['players'][player] = self._players[player].to_dict()
        
        with open(filename, 'w') as wfile:
            json.dump(dct, wfile)
    
    def new_player(self, uid, uname):
        player = Player(self, uid)
        player._username = uname
        self._players[uid] = player
        return player
    
    def get_player(self, player):
        """ Tries to find a player either by ID or by username. """
        
        if isinstance(player, int):
            player = str(player)
        elif not isinstance(player, str):
            raise NotImplementedError('Cannot find player from {0} type!'.format(type(player)))

        if player in self.players:
            return self.players[player]

        for uid in self.players:
            if self.players[uid].username == player:
                return self.players[uid]

        return None
    
    @property
    def players(self):
        return self._players
    
    def add_owner(self, owner):
        if not owner in self._owners:
            self._owners.append(owner)
    
    def remove_owner(self, owner):
        if owner in self._owners:
            self._owners.remove(owner)
    
    def is_owner(self, player):
        if isinstance(player, Player):
            return player.uid in self._owners
        elif isinstance(player, str) or isinstance(player, int):
            return str(player) in self._owners
        else:
            raise NotImplementedError('Cannot check ownership for {0} type!'.format(player))