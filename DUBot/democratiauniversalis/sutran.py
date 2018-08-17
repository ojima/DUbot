class Sutran:
    """ the game of Sutran """

    def __init__(self):
        board = []
        for _ in range(9):
            board.append([ None for _ in range(9) ])
        self._board = board

        self._starter = Player(0, self)
        self._second = Player(1, self)

        for i in range(9):
            if(i < 2 or i > 6):
                self._starter.place("knight", (0, i))
                self._second.place("knight", (8, i))
            else:
                self._starter.place("pawn", (0, i))
                self._second.place("pawn", (8, i))

    @property
    def board(self):
        return self._board

    def move(self, player, start, end):
        """ moves a unit and returns true if it moved and false if it couldn't """
        if self._board[start[0]][start[1]] != None and self._board[start[0]][start[1]].owner() == player:
            ret = self._board[start[0]][start[1]].move(end)
            self.overruns()
            return ret
        return False

    def overruns(self):
        """ clears the board out of overruns """
        for i in range(1, 8):
            for j in range(1, 8):
                unit = self._board[i][j]
                if unit != None:
                    if self._board[i + 1][j].owner() != unit.owner() and self._board[i - 1][j].owner() != unit.owner() and self._board[i][j - 1].owner() != unit.owner() and self._board[i][j + 1].owner() != unit.owner():
                        self._board[i][j] = None
                        unit.owner().removeUnit(unit)

    def victories(self):
        """ returns 0 if the game should still continue, -1 if both players lost, 1 if the starting won, and 2 if he lost """
        player1 = self._starter.remainingUnits()
        player2 = self._second.remainingUnits()
        if player1 > 3 and player2 > 3:
            return 0
        if player1 <= 3 and player2 <= 3:
            return -1
        if player2 < 3:
            return 1
        if player1 < 3:
            return 2

    def canCapture(self, location):
        """returns True if the piece in the location can be captured by the enemy and false otherwise"""
        unit = self._board[location[0]][location[1]]
        if(unit == None):
            return False
        friendly = 0
        enemies = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if self._board[location[0] + i][location[1] + j] != False:
                    if self._board[location[0] + i][location[1] + j].owner() == unit.owner():
                        friendly += 1
                    if self._board[location[0] + i][location[1] + j].owner() != unit.owner() and self._board:
                        enemies += 1
        if enemies > friendly:
            return True
        return False

    def Capture(self, player, start, capture, other = None):
        """tries to capture the unit in capture and in other via the unit from start and returns True is sucessful and False if it cannot be captures"""
        startUnit = self._board[start[0]][start[1]]
        captureUnit = self._board[capture[0]][capture[1]]
        otherUnit = self._board[other[0]][other[1]]
        if otherUnit != None and otherUnit.owner() == player:
            return False
        if startUnit.owner() != player or captureUnit.owner() == player:
            return False
        startUnit.owner().toReserve(start)
        captureUnit.owner().removeUnit(captureUnit)
        if(otherUnit != None):
            otherUnit.owner.removeUnit(otherUnit)

class Player:
    """ a player in Sutran """

    def __init__(self, pid, game):
        self._id = pid
        self._game = game
        self._units = []
        self._reserve = []
        for _ in range(11):
            self._reserve.append(Pawn(self))
        for _ in range(6):
            self._reserve.append(Knight(self))

    def __eq__(self, other):
        if not isinstance(other, Player):
            raise NotImplementedError('Cannot compare player to {0} type.'.format(type(other)))
        if self._id == other._id:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def remainingUnits(self):
        return len(self._units) + len(self._reserve)

    def removeUnit(self, unit):
        if unit in self._units:
            self._units.remove(unit)
            return True
        if unit in self._reserve:
            self._reserve.remove(unit)
            return True
        return False

    def toReserve(self, unit):
        if unit in self._units:
            self._units.remove(unit)
            unit.setLocation(None)
            self._reserve.append(unit)
            return True
        return False

    def canPlace(self, typ):
        for unit in self._reserve:
            if unit.type() == typ:
                return True
        return False

    def place(self, typ, location):
        if self.canPlace(typ) and self._game.board[location[0]][location[1]] == None:
            for unit in self._reserve:
                if unit.type == typ:
                    self._reserve.remove(unit)
                    unit.setLocation(location)
                    self._game.board[location[0]][location[1]] = unit
                    self._units.append(unit)
                    return True
        return False

    @property
    def game(self):
        return self._game

class Unit:
    """ Unit base class """

    def __init__(self, owner, location = None):
        self._owner = owner
        self._location = location

    def canMove(self, location):
        if self._owner.game.board[location[0]][location[1]] == None:
            return True
        return False

    def move(self, location):
        if self.canMove(location):
            self._owner.game.board[self._location[0]][self._location[1]] = None
            self._location = location
            self._owner.game.board[location[0]][location[1]] = self
            return True
        
        return False

    def setLocation(self, location):
        self._location = location

    def owner(self):
        return self._owner

    @property
    def type(self):
        return None

    def __str__(self):
        return self.type

    def __repr__(self):
        return self.type

class Pawn(Unit):
    """ The Pawn Unit """

    def canMove(self, location):
        if not super().canMove(location):
            return False
        distance = abs(location[0] - self._location[0]) + abs(location[1] - self._location[1])
        if distance <= 1: return True
        return False

    @property
    def type(self):
        return "pawn"

class Knight(Unit):
    """ The Knight Unit """

    def canMove(self, location):
        if not super().canMove(location):
            return False
        distance = abs(location[0] - self._location[0]) + abs(location[1] - self._location[1])
        if distance <= 2: return True
        return False

    @property
    def type(self):
        return "knight"
