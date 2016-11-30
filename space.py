from enum import Enum
# Enum of valid spaces
import portalUtilities as portalUtil#several misc functions that are unrelated to functionality or not specific to AI
SpaceType = Enum("SpaceType", "empty softBlock hardBlock")

# get a list of all coords that will be hit by the bomb at position x,y
# note that this will fail without the board in the global namespace (currently maintained by ratchetAI and included in const.py)
def checkBombAffectedCoords(x,y,bombPierce,bombRange,board,gameState):
    boardSize = len(board)
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
                
                #check if we are moving through a portal
                prevSpace = board[curX-direction][curY] if direction <= 1 else board[curX][curY-(direction-4)]
                if (board[curX][curY].containsPortal):
                    newSpace = portalUtil.canTraversePortal(board,gameState,prevSpace,board[curX][curY])
                    if (newSpace[0]):
                        curX = newSpace[1].x
                        curY = newSpace[1].y
                    
                affectedCoords.append((curX,curY))
                if (board[curX][curY].type in (SpaceType.softBlock, SpaceType.hardBlock)):
                    curPierce -= 1
                    if (curPierce < 0):
                        break
    return affectedCoords

# basic class containing info on a single unit space, including what that space is, and whether or not it is in range of an upcoming or active explosion Trail
class Space():
    def __str__(self):
        return self.getState() + " at: " + str(self.x) + ", " + str(self.y)

    def __repr__(self):
        return self.__str__()

    def __init__(self,gameState,x,y,board):
        boardSize = len(board)
        # set whether or not the player or the opponent is currently on this space
        def checkContainsEitherPlayer():
            return int(gameState['player']['x']) == self.x and int(gameState['player']['y']) == self.y, int(gameState['opponent']['x']) == self.x and int(gameState['opponent']['y']) == self.y

        # set type according to gameState
        def checkType():
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
        
        # set whether or not a portal is currently on this space
        def checkContainsPortal():
            portalKeys = gameState['portalMap'].keys()
            for coord in portalKeys:
                portalX = int(coord.split(",")[0])
                portalY = int(coord.split(",")[1])
                if (portalX ==self.x and portalY == self.y):
                    return True,coord
            return False,None

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
        self.containsPortal,self.containedPortalCoord = checkContainsPortal()
        self.containsTrail = checkContainsTrail()
        self.containsPlayer,self.containsOpponent = checkContainsEitherPlayer()
        
    #print a 3-character representation of this Space's current state
    def getState(self):
        returnString = ""
        if (self.type == SpaceType.hardBlock):
            returnString += "|"
        if (self.type == SpaceType.softBlock):
            returnString += "x"
        if (self.containsBomb):
            returnString += "B"
        if (self.containsOpponent):
            returnString += "O"
        if (self.containsPlayer):
            returnString += "P"
        if (self.containsTrail):
            returnString += "*"
        if (self.containsUpcomingTrail):
            returnString += "~"
        if (returnString == ""):
            returnString = "-"
        if (len(returnString) == 1):
            returnString = " " + returnString + " "
        else:
            returnString = returnString[1] + returnString[0] + returnString[1]
        return returnString
        

    def initializeLateProperties(self,gameState,board):
        boardSize = len(board)
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
                bombAffectedCoords = checkBombAffectedCoords(bombX,bombY,bombPierce,bombRange,board,gameState)
                if ((self.x,self.y) in bombAffectedCoords):
                    return (True,bombTurnsRemaining)
            return (False,-1)

        # todo: may be thrown off if bomb range and pierce count are upgraded after placing (depending on game mechanics)
        self.containsUpcomingTrail,self.turnsUntilUpcomingTrail = checkContainsUpcomingTrail()
