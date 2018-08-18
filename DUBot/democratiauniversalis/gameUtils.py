def toLocation(chessNotation):
    """converts a chess notation string to a location tuple"""
    y = ord(chessNotation[0])-ord('a')
    x = int(chessNotation[1:])-1
    return (x, y)

def expectedResult(A, B):
    """
    Calculate expected score of A in a match against B
    :param A: Elo rating for player A
    :param B: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((B - A) / 400))


def updateElo(old, exp, score, k=32):
    """
    Calculate the new Elo rating for a player
    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + k * (score - exp)

def elo(ratings, victor, k=32):
    """returns the updated elo score after a single match between two players"""
    expected = expectedResult(ratings[0], ratings[1])
    expectations = (expected, 1-expected)
    return (updateElo(ratings[0], expectations[0], victor, k=k), updateElo(ratings[1], expectations[1], 1-victor, k=k))
