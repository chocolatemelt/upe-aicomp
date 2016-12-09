import portalUtilities as portalUtil#several misc functions that are unrelated to functionality or not specific to AI
from portalUtilities import SpaceType, fireTurnMap

def checkBombAffectedCoords(x,y,bombPierce,bombRange,board,gameState):
    """get a list of all coords that will be hit by the bomb at position x,y
      note that this will fail without the board in the global namespace (currently maintained by ratchetAI and included in const.py)"""
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

class Space():
    """basic class containing info on a single unit space, including what that space is, and whether or not it is in range of an upcoming or active explosion Trail"""
    def __str__(self):
        """string value of class"""
        return self.__repr__()

    def __repr__(self):
        """representation of class"""
        return self.getState() + " at: " + str(self.x) + ", " + str(self.y)

    def __init__(self,gameState,x,y,board):
        """constructor: init properties that do not depend on other spaces' properties"""
        boardSize = len(board)
        
        def checkContainsEitherPlayer():
            """set whether or not the player or the opponent is currently on this space"""
            return int(gameState['player']['x']) == self.x and int(gameState['player']['y']) == self.y, int(gameState['opponent']['x']) == self.x and int(gameState['opponent']['y']) == self.y

        def checkType():
            """set type according to gameState"""
            if (int(gameState['hardBlockBoard'][self.x*boardSize + self.y]) == 1):
                return SpaceType.hardBlock
            if (int(gameState['softBlockBoard'][self.x*boardSize + self.y]) == 1):
                return SpaceType.softBlock
            return SpaceType.empty

        def checkContainsBomb():
            """set whether or not a bomb is currently on this space"""
            bombKeys = gameState['bombMap'].keys()
            for coord in bombKeys:
                bombX = int(coord.split(",")[0])
                bombY = int(coord.split(",")[1])
                if (bombX ==self.x and bombY == self.y):
                    return True
            return False
        
        def checkContainsPortal():
            """set whether or not a portal is currently on this space"""
            portalKeys = gameState['portalMap'].keys()
            for coord in portalKeys:
                portalX = int(coord.split(",")[0])
                portalY = int(coord.split(",")[1])
                if ((portalX ==self.x and portalY == self.y) and (gameState['portalMap'][coord] != {})):
                    return True,coord
            return False,None

        def checkContainsTrail():
            """set whether or not an explosion Trail is currently on this space"""
            trailKeys = gameState['trailMap'].keys()
            for coord in trailKeys:
                trailX = int(coord.split(",")[0])
                trailY = int(coord.split(",")[1])
                if (trailX ==self.x and trailY == self.y):
                    return True
            return False
        
        def checkIsCenterSpace():
            """set whether or not this space is in the center of the grid"""
            boardSize = len(board)
            if (boardSize % 2 == 1):
                return (self.x == boardSize // 2 and self.y == boardSize // 2)
            return ((self.x == boardSize/2 or self.x == boardSize/2 - 1) and (self.y == boardSize/2 or self.y == boardSize/2 - 1))

        self.x = x
        self.y = y
        self.type = checkType()
        self.containsBomb = checkContainsBomb()
        try:
            self.containsPortal,self.containedPortalCoord = checkContainsPortal()
        except:
            self.containsPortal = False
        self.containsTrail = checkContainsTrail()
        self.containsPlayer,self.containsOpponent = checkContainsEitherPlayer()
        self.isCenterSpace = checkIsCenterSpace()
        
    def getState(self):
        """print a 3-character representation of this Space's current state"""
        returnString = ""
        if (self.type == SpaceType.hardBlock):
            returnString += ("|" if not self.containsPortal else "S")
        if (self.type == SpaceType.softBlock):
            returnString += ("x" if not self.containsPortal else "s")
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
        """init properties that depend on other spaces to be initialized"""
        
        def checkContainsUpcomingFire():
            """determine whether or not this Space will be occupied by apocalypse fire in a few turns"""
            maxLookaheadTurns = 4 #subtract 2 from this value to get the actual number of turns before upcoming trail is toggled
            fireTurn = fireTurnMap[self.x][self.y]
            if (fireTurn - gameState['moveNumber'] <= maxLookaheadTurns):
                return True, fireTurn - gameState['moveNumber']
            return False, -1

        def checkContainsUpcomingTrail():
            """set whether or not an explosion Trail will soon be on this space"""
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

        # todo: can be abused if bomb range and pierce count are upgraded after placing
        self.containsUpcomingTrail,self.turnsUntilUpcomingTrail = checkContainsUpcomingTrail()
        
        containsUpcomingFire,turnsUntilUpcomingFire = checkContainsUpcomingFire()
        if ((containsUpcomingFire) and turnsUntilUpcomingFire <= 0):
            self.containsTrail = True
            
        elif (containsUpcomingFire):
            if ((not self.containsUpcomingTrail) or (self.turnsUntilUpcomingTrail > turnsUntilUpcomingFire)):
                self.containsUpcomingTrail = True
                self.turnsUntilUpcomingTrail = turnsUntilUpcomingFire