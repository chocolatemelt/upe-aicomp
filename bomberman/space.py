from enum import Enum
try: #trick eclipse into thinking we're importing now, when in reality we import in __init__
    from .constants import board,boardSize
except:
    pass
# Enum of valid spaces
SpaceType = Enum("SpaceType", "empty softBlock hardBlock")

# get a list of all coords that will be hit by the bomb at position x,y
# note that this will fail without the board in the global namespace (currently maintained by ratchetAI and included in const.py)
def checkBombAffectedCoords(x,y,bombPierce,bombRange):
    from .constants import board,boardSize
    #print("'check bomb affected' called. board state: ")
    #print(board)
    affectedCoords = [(x,y)] #  the bomb square itself will be hit no matter what
    # check negative x (left) then positive x (right) squares, then negative y (up) and then finally positive y (down) squares
    for direction in range(-1, 6, 2):
        curPierce = bombPierce
        curX = x
        curY = y
        for _ in range(bombRange):
            if (direction <= 1):
                curX += direction
            else:
                curY += direction-4 # offset of 4 so that -1 -> 1 account for x increments, and 3 -> 5 (minus 4) account for y increments
            if curX >= 0 and curX < boardSize and curY >= 0 and curY < boardSize:
                affectedCoords.append((curX,curY))
                #print("curX: " + str(curX) + ", curY: " + str(curY))
                #print(board)
                if (board[curX][curY].type in (SpaceType.softBlock, SpaceType.hardBlock)):
                    curPierce -= 1
                    if (curPierce < 0):
                        break
    return affectedCoords

# basic class containing info on a single unit space, including what that space is, and whether or not it is in range of an upcoming or active explosion Trail
class Space():
    def __str__(self):
        return "Space at: " + str(self.x) + ", " + str(self.y)

    def __repr__(self):
        return self.__str__()

    def __init__(self,gameState,x,y):
        from .constants import board,boardSize
        # set whether or not the player or the opponent is currently on this space
        def checkContainsEitherPlayer():
            return int(gameState['player']['x']) == self.x and int(gameState['player']['y']) == self.y, int(gameState['opponent']['x']) == self.x and int(gameState['opponent']['y']) == self.y

        # set type according to gameState
        def checkType():
            if (self.x == 3 and self.y == 1):
                print(gameState['softBlockBoard'])
                print(int(gameState['softBlockBoard'][self.x*boardSize + self.y]))
            '''print(self.y*boardSize + self.x)
            if (int(gameState['hardBlockBoard'][self.x*boardSize + self.y]) != 1):
                print("found not hard block")'''
            if (int(gameState['hardBlockBoard'][self.x*boardSize + self.y]) == 1):
                return SpaceType.hardBlock
            if (int(gameState['softBlockBoard'][self.x*boardSize + self.y]) == 1):
                return SpaceType.softBlock
            return SpaceType.empty

        # set whether or not a bomb is currently on this space
        def checkContainsBomb():
            bombKeys = gameState['bombMap'].keys()
            for coord in bombKeys:
                bombX = int(coord.split(",")[0])
                bombY = int(coord.split(",")[1])
                if (bombX ==self.x and bombY == self.y):
                    return True
            return False

        # set whether or not an explosion Trail is currently on this space
        def checkContainsTrail():
            trailKeys = gameState['trailMap'].keys()
            for coord in trailKeys:
                trailX = int(coord.split(",")[0])
                trailY = int(coord.split(",")[1])
                if (trailX ==self.x and trailY == self.y):
                    return True
            return False

        self.x = x
        self.y = y
        self.type = checkType()
        self.containsBomb = checkContainsBomb()
        self.containsTrail = checkContainsTrail()
        self.containsPlayer,self.containsOpponent = checkContainsEitherPlayer()

    def initializeLateProperties(self,gameState):
        # set whether or not an explosion Trail will soon be on this space
        def checkContainsUpcomingTrail():
            # todo: repeat code from checkContainsBomb
            bombKeys = gameState['bombMap'].keys()
            for coord in bombKeys:
                bombX = int(coord.split(",")[0])
                bombY = int(coord.split(",")[1])
                bombPlayer = gameState['bombMap'][coord]['owner']
                bombTurnsRemaining = gameState['bombMap'][coord]['tick']
                if (bombPlayer == gameState['playerIndex']):
                    bombPierce = gameState['player']['bombPierce']
                    bombRange = gameState['player']['bombRange']
                else:
                    bombPierce = gameState['opponent']['bombPierce']
                    bombRange = gameState['opponent']['bombRange']
                bombAffectedCoords = checkBombAffectedCoords(bombX,bombY,bombPierce,bombRange)
                if ((self.x,self.y) in bombAffectedCoords):
                    return (True,bombTurnsRemaining)
            return (False,-1)

        # todo: may be thrown off if bomb range and pierce count are upgraded after placing (depending on game mechanics)
        self.containsUpcomingTrail,self.turnsUntilUpcomingTrail = checkContainsUpcomingTrail()
