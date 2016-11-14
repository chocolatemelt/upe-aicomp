from enum import Enum
from .constants import *

# Enum of valid spaces
SpaceType = Enum("SpaceType", "empty softBlock hardBlock")

# basic class containing info on a single unit space, including what that space is, and whether or not it is in range of an upcoming or active explosion Trail
class Space():
    def __str__(self):
        return "Space at: " + str(self.x) + ", " + str(self.y)

    def __repr__(self):
        return self.__str__()

    def __init__(self,gameState,x,y):
        # set whether or not the player or the opponent is currently on this space
        def checkContainsEitherPlayer():
            return int(gameState['player']['x']) == self.x and int(gameState['player']['y']) == self.y, int(gameState['opponent']['x']) == self.x and int(gameState['opponent']['y']) == self.y

        # set type according to gameState
        def checkType():
            if (int(gameState['hardBlockBoard'][self.y*boardSize + self.x]) == 1):
                return SpaceType.empty
            if (int(gameState['softBlockBoard'][self.y*boardSize + self.x]) == 1):
                return SpaceType.softBlock
            return SpaceType.hardBlock

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
