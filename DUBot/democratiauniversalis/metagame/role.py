import datetime

class Role:

    def __init__(self, name = None):
        self._name = name
        self._termstart = None
        self._termlength = None
        self._salary = 0

    def from_dict(self, dct):
        self._name = dct['name']
        self._termstart = datetime.datetime.strptime(dct['start'], '%d-%m-%Y')
        self._termlength = datetime.timedelta(days = dct['length'])

        if 'salary' in dct:
            self._salary = dct['salary']

    def to_dict(self) -> dict:
        dct = { }

        dct['name'] = self._name
        dct['start'] = self._termstart.strftime('%d-%m-%Y')
        dct['length'] = self._termlength.days
        dct['salary'] = self._salary

        return dct

    def has_expired(self, t = None) -> bool:
        """ Returns whether this role has expired yet. Terms of negative length are considered indefinite terms. """
        if self._termlength.days < 0:
            return False

        if t is None:
            t = datetime.datetime.now()

        return (t - self._termstart) >= self._termlength

    @property
    def name(self) -> str:
        return self._name

    @property
    def term_start(self) -> datetime.datetime:
        return self._termstart

    @term_start.setter
    def term_start(self, ts):
        self._termstart = ts

    @property
    def term_length(self) -> datetime.timedelta:
        return self._termlength

    @term_length.setter
    def term_length(self, tl):
        self._termlength = tl

    @property
    def term_end(self) -> datetime.datetime:
        return self._termstart + self._termlength

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, val):
        self._salary = val
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Role):
            return self.name == other.name
        else:
            raise NotImplementedError('Cannot compare Role to {0}'.format(type(other)))