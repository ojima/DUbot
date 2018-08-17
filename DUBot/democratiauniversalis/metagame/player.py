from democratiauniversalis.metagame.role import Role

class Player:

    # List of default values for settings
    settings = {
        "remind-me" : False
    }

    def __init__(self, game, uid):
        self._game = game
        self._uid = uid
        self._username = None
        self._roles = [ ]
        self._settings = Player.settings

    def from_dict(self, dct):
        self._username = dct['username']
        self._roles = [ ]

        for r in dct['roles']:
            s = Role()
            s.from_dict(r)
            self._roles.append(s)
        
        for s in dct['settings']:
            self._settings[s] = dct['settings'][s]

    def to_dict(self):
        dct = { }

        dct['username'] = self._username
        dct['roles'] = [ ]

        for role in self._roles:
            dct['roles'].append(role.to_dict())

        dct['settings'] = self._settings

        return dct

    def set_setting(self, setting, value):
        if not setting in Player.settings:
            raise KeyError('Invalid key for player setting {0}'.format(setting))
        if not type(value) == type(Player.settings[setting]):
            raise ValueError('Invalid value {1} for player setting {0}'.format(setting, value))
        self._settings[setting] = value

    def get_setting(self, setting):
        if not setting in Player.settings:
            return None
        if not setting in self._settings:
            return Player.settings[setting]
        return self._settings[setting]

    def add_role(self, role):
        self._roles.append(role)

    def remove_role(self, role):
        for r in self._roles:
            if r == role:
                self._roles.remove(r)

    def has_role(self, role):
        for r in self._roles:
            if r == role:
                return True
        return False

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def username(self) -> str:
        return self._username

    @property
    def roles(self) -> list:
        return self._roles

    def __eq__(self, other):
        if isinstance(other, int):
            return int(self._uid) == other
        elif isinstance(other, str):
            return self._uid == other or self._username == other
        elif isinstance(other, Player):
            return self._uid == other._uid
        else:
            raise NotImplementedError('Cannot compare player instance to {0}.'.format(type(other)))