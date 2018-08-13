import json
import time

from democratiauniversalis.prototypes import Runnable, Saveable
import multiprocessing as Mp

class Banking(Runnable, Saveable):

    def __init__(self, queue):
        super().__init__()

        self._accounts = { }
        self._transactions = { }

        self._lock = Mp.Lock()
        self._outqueue = queue

        self._next_aid = 0
        self._next_tid = 0

    def update(self):
        while not self.queue.empty():
            event = self.queue.get()

            if event['type'] == 'save':
                self.save(event['filename'])

    def load(self, filename):
        self.log('Loading banking state.')

        with open(filename, 'r') as fp:
            dct = json.load(fp)

        accs = dct['accounts']
        for uid in accs:
            if int(uid) >= self._next_aid:
                self._next_aid = int(uid) + 1

            acc = accs[uid]
            A = Account(int(uid), acc['name'], acc['owner'])
            A.from_dct(acc)

    def save(self, filename):
        self.log('Saving banking state.')

        dct = { "accounts" : {}, "transactions" : {} }

        with open(filename, 'w') as fp:
            json.dump(dct, fp)

    def new_account(self, name, owner):
        """ Create a new account for the player. """
        A = Account(self._next_id, name, owner)
        self._next_aid += 1

        self._accounts.append(A)

        self.log('New banking account [{1}] {0} for user <{2}>'.format(A.name, A.aid, owner))

    def get_accounts(self, pid):
        """ Returns an (id, name, balance) tuple array for all bank accounts to which [pid] has access. """
        res = []

        for acc in self._accounts:
            A = self._accounts[acc]
            if A.has_user(pid):
                res.append((A.aid, A.name, A.balance))

        return res

    def get_account(self, pid, aid):
        """ Returns the account associated with [aid] if and only if player [pid] has access. """
        if not aid in self._accounts:
            return None, 'Account does not exist'

        A = self._accounts[aid]
        if not A.has_user(pid):
            return None, 'User has no access'

        return A, 'Success'

    def transfer(self, pid, aid, target, amount, details = ''):
        if not aid in self._accounts:
            return None, 'Failed to find account {0}'.format(aid)

        acc = self._accounts[aid]
        if not acc.has_user(pid):
            return None, 'User has no access'

        if amount < 0:
            return None, 'Invalid transfer amount'

        if acc.balance < amount:
            return None, 'Insufficient balance'

        if not target in self._accounts:
            return None, 'Failed to find target {0}'.format(target)

        tgt = self._accounts[target]
        acc.add_balance(-amount)
        tgt.add_balance(+amount)
        
        T = Transaction(self._next_tid, time.localtime(), aid, target, amount, details)
        self._transactions[self._next_tid] = T
        self._next_tid += 1
        
        return T, 'Success'

    @property
    def name(self):
        return 'banking'

class Account:

    def __init__(self, aid, name, owner):
        self._aid = aid
        self._name = name
        self._owner = owner
        self._users = [ owner ]
        self._balance = 0

    def to_dict(self):
        res = { }
        res['name'] = self._name
        res['owner'] = self._owner
        res['users'] = [ ]
        for user in self._users:
            res['users'].append(user)
        res['balance'] = self._balance

        return res

    def from_dict(self, dct):
        self._name = dct['name']
        self._owner = dct['owner']
        self._users = dct['users']
        self._balance = dct['balance']

    def add_user(self, user):
        if not user in self._users:
            self._users.append(user)

    def del_user(self, user):
        if user in self._users:
            self._users.remove(user)

    def has_user(self, user):
        return user in self._users
    
    def add_balance(self, val):
        self._balance += val
    
    @property
    def aid(self):
        return self._aid

    @property
    def name(self):
        return self._name

    @property
    def users(self):
        return self._users

    @property
    def owner(self):
        return self._owner

    @property
    def balance(self):
        return self._balance
    
    # --------------------
    # OPERATOR OVERLOADING
    # --------------------

    def __radd__(self, other):
        if isinstance(other, Account):
            return self._balance + other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance + other
        else:
            raise NotImplementedError("Failed to evaluate '{0} + {1}' ({1}.__radd__): operation not implemented.".format(type(other), type(self)))

    def __add__(self, other):
        if isinstance(other, Account):
            return self._balance + other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance + other
        else:
            raise NotImplementedError("Failed to evaluate '{0} + {1}' ({0}.__add__): operation not implemented.".format(type(self), type(other)))

    def __mul__(self, other):
        if isinstance(other, Account):
            return self._balance * other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance * other
        else:
            raise NotImplementedError("Failed to evaluate '{0} * {1}' ({0}.__mul__): operation not implemented.".format(type(self), type(other)))

    def __div__(self, other):
        if isinstance(other, Account):
            return self._balance / other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance / other
        else:
            raise NotImplementedError("Failed to evaluate '{0} + {1}' ({0}.__div__): operation not implemented.".format(type(self), type(other)))

    def __eq__(self, other):
        if isinstance(other, Account):
            return self._balance == other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance == other
        else:
            raise NotImplementedError("Failed to evaluate '{0} == {1}' ({0}.__eq__): operation not implemented.".format(type(self), type(other)))

    def __ne__(self, other):
        if isinstance(other, Account):
            return self._balance != other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance != other
        else:
            raise NotImplementedError("Failed to evaluate '{0} > {1}' ({0}.__ne__): operation not implemented.".format(type(self), type(other)))

    def __lt__(self, other):
        if isinstance(other, Account):
            return self._balance < other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance < other
        else:
            raise NotImplementedError("Failed to evaluate '{0} < {1}' ({0}.__lt__): operation not implemented.".format(type(self), type(other)))

    def __gt__(self, other):
        if isinstance(other, Account):
            return self._balance > other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance > other
        else:
            raise NotImplementedError("Failed to evaluate '{0} > {1}' ({0}.__gt__): operation not implemented.".format(type(self), type(other)))

    def __le__(self, other):
        if isinstance(other, Account):
            return self._balance <= other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance <= other
        else:
            raise NotImplementedError("Failed to evaluate '{0} <= {1}' ({0}.__le__): operation not implemented.".format(type(self), type(other)))

    def __ge__(self, other):
        if isinstance(other, Account):
            return self._balance >= other._balance
        elif isinstance(other, int) or isinstance(other, float):
            return self._balance >= other
        else:
            raise NotImplementedError("Failed to evaluate '{0} >= {1}' ({0}.__ge__): operation not implemented.".format(type(self), type(other)))

class Transaction:

    def __init__(self, tid, date, from_id, to_id, amount, details = ''):
        self._tid = tid

        if isinstance(date, str):
            self._date = time.strptime(date, '%d/%m/%Y')
        elif isinstance(date, time.struct_time):
            self._date = date
        else:
            raise NotImplementedError('Cannot convert {0} to transaction date.'.format(type(date)))

        self._from = from_id
        self._to = to_id
        self._amount = amount
        self._details = details

    @property
    def tid(self):
        return self._tid

    @property
    def date(self):
        return self._date

    @property
    def to_id(self):
        return self._to

    @property
    def from_id(self):
        return self._from

    @property
    def amount(self):
        return self._amount

    @property
    def details(self):
        return self._details