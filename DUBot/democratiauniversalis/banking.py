import json
import time

from democratiauniversalis.prototypes import Runnable, Saveable
import multiprocessing as Mp

def str_to_id(s : str) -> int:
    """ Turns a [0123 4567] ID string into an integer """
    return int(s.strip().replace(' ', ''))

def str_to_balance(s : str) -> int:
    """ Turns a [1,234.56 BB] balance string into an integer """
    try:
        return int(s.strip().replace('BB', '').replace(',', '').replace('.', '').strip())
    except:
        print('Failed to interpret balance \'{0:s}\'.'.format(s))
        return 0

def id_to_str(s : int) -> str:
    """ Turns an ID integer into a [0123 4567] string """
    if isinstance(s, str): s = int(s)

    l = s % 10000
    h = int((s - l) / 10000)
    return '{0:04d} {1:04d}'.format(h, l)

def balance_to_str(s : int) -> str:
    """ Turns a balance integer into a [1,234.56 BB] string """
    if isinstance(s, str): s = int(s)

    b = float(s / 100.0)
    return '{0:.2f} BB'.format(b)

class Banking(Runnable, Saveable):

    def __init__(self, queue, filename):
        super().__init__()

        self._accounts = { }
        self._transactions = { }

        self._lock = Mp.Lock()
        self._outqueue = queue

        self._next_aid = 0
        self._next_tid = 0

        self._filename = filename

    def update(self):
        while not self.queue.empty():
            event = self.queue.get()

            if event['type'] == 'save':
                self.save(self._filename)
            elif event['type'] == 'new':
                pid = event['pid']
                aid = self._next_aid
                self._next_aid += 1
                name = event['name']

                acc = Account(aid, name, pid)
                self._accounts[aid] = acc

                reply = 'Created new account *{0}* with ID `{1}`.'.format(name, id_to_str(aid))

                self._outqueue.put({ 'to' : event['channel'], 'message' : reply })
                self.save(self._filename)
            elif event['type'] == 'balance':
                pid = event['pid']

                accs = self.get_accounts(pid)
                if len(accs) == 0:
                    self._outqueue.put({ 'to' : event['channel'], 'message' : 'You do not have any bank accounts linked to your account.' })
                    return

                reply = 'Your accounts:'
                total = 0
                for uid, name, balance in accs:
                    total += balance
                    reply += '\n`{0}` {1}: {2}'.format(id_to_str(uid), name, balance_to_str(balance))

                reply += '\n----------\nTotal: {0}'.format(balance_to_str(total))
                self._outqueue.put({ 'to' : event['channel'], 'message' : reply })
            elif event['type'] == 'transfer':
                pid = event['pid']
                from_id = str_to_id(event['from'])
                to_id = str_to_id(event['to'])
                amount = str_to_balance(event['amount'])
                
                trs, err = self.transfer(pid, str(from_id), str(to_id), amount, event['details'])
                
                if trs is None:
                    reply = 'Failed to complete transaction: {0}.'.format(err)
                    self._outqueue.put({ 'to' : event['channel'], 'message' : reply })
                    return
                
                ac1 = self._accounts[trs.from_id]
                ac2 = self._accounts[trs.to_id]
                reply = 'A transaction has been processed for your account\n{0}'.format(trs.to_string(ac1.name, ac2.name))
                
                self._outqueue.put({ 'to' : event['channel'], 'message' : reply })
                self.save(self._filename)

    def load(self, filename):
        self.log('Loading banking state.')

        with open(filename, 'r') as fp:
            dct = json.load(fp)

        accs = dct['accounts']
        for aid in accs:
            if int(aid) >= self._next_aid:
                self._next_aid = int(aid) + 1

            acc = accs[aid]
            A = Account(int(aid), acc['name'], acc['owner'])
            A.from_dict(acc)
            self._accounts[aid] = A
        
        trs = dct['transactions']
        for tid in trs:
            if int(tid) >= self._next_tid:
                self._next_tid = int(tid) + 1

            tr = trs[tid]
            T = Transaction()
            T.from_dict(tr)
            self._transactions[tid] = T

    def save(self, filename):
        self.log('Saving banking state.')

        dct = { "accounts" : {}, "transactions" : {} }

        for aid in self._accounts:
            dct['accounts'][aid] = self._accounts[aid].to_dict()

        for tid in self._transactions:
            dct['transactions'][tid] = self._transactions[tid].to_dict()

        with open(filename, 'w') as fp:
            json.dump(dct, fp, indent = 2)

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
    
    def get_owners(self, aid):
        if not aid in self._accounts:
            return None
        
        return self._accounts[aid].users
    
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

    def __init__(self, tid = None, date = None, from_id = None, to_id = None, amount = None, details = ''):
        self._tid = tid
        
        if date is None:
            self._date = None
        elif isinstance(date, str):
            self._date = time.strptime(date, '%d/%m/%Y')
        elif isinstance(date, time.struct_time):
            self._date = date
        else:
            raise NotImplementedError('Cannot convert {0} to transaction date.'.format(type(date)))

        self._from = from_id
        self._to = to_id
        self._amount = amount
        self._details = details

    def from_dict(self, dct):
        self._from = dct['from']
        self._to = dct['to']
        self._amount = dct['amount']
        self._date = time.strptime(dct['date'], '%d/%m/%Y')
        if 'details' in dct:
            self._details = dct['details']
        else:
            self._details = ''

    def to_dict(self):
        res = { }

        res['from'] = self._from
        res['to'] = self._to
        res['amount'] = self._amount
        res['date'] = time.strftime('%d/%m/%Y', self._date)
        if len(self._details) > 0:
            res['details'] = self._details

        return res
    
    def to_string(self, name1 = '', name2 = ''):
        return 'Transaction ID: `{0}`\n\
Transaction date: {1}\n\
From: *{4}*\n\
ID: `{2}`\n\n\
To: *{5}*\n\
ID: `{3}`\n\n\
Description: {7}\n\n\
Amount: {6}'.format(id_to_str(int(self.tid)),
                    time.strftime('%d/%m/%Y', self._date),
                    id_to_str(int(self.from_id)),
                    id_to_str(int(self.to_id)),
                    name1, name2,
                    balance_to_str(self.amount),
                    self.details)
    
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