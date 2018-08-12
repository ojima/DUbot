from democratiauniversalis.metagame.role import Role

class Player:
    def __init__(self, game, uid):
        self._game = game
        self._uid = uid
        self._username = None
        self._roles = [ ]
    
    def from_dict(self, dct):
        self._username = dct['username']
        self._roles = [ ]
        
        for r in dct['roles']:
            s = Role()
            s.from_dict(r)
            self._roles.append(s)
    
    def to_dict(self):
        dct = { }
        
        dct['username'] = self._username
        dct['roles'] = [ ]
        
        for role in self._roles:
            dct['roles'].append(role.to_dict())
        
        return dct
    
    @property
    def uid(self) -> str:
        return self._uid
    
    @property
    def username(self) -> str:
        return self._username
    
    def __eq__(self, other):
        if isinstance(other, int):
            return int(self._uid) == other
        elif isinstance(other, str):
            return self._uid == other or self._username == other
        elif isinstance(other, Player):
            return self._uid == other._uid
        else:
            raise NotImplementedError('Cannot compare player instance to {0}.'.format(type(other)))