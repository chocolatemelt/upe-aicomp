"""basic AI designed to overcome basic, common circumstances in order to beat random the qualifier bot"""
import requests #needed to send and receive data from the server
import json #allows us to test the game at a single point in time by reading / writing JSON data to a file
import os.path #allows us to check if JSON file exists before attempting to read data from it when in debug mode
from space import * #custom space class containing information about a given board position

debugMode = True #flag which instructs the program to write gameState to JSON file each turn for future processing

# networking constants
username = "kzhaaang"
devkey = "5823b8c404d7ce4a44c37ab4"
qualifierURL = "http://aicomp.io/api/games/practice" # practice qualifier bot
rankedURL = "http://aicomp.io/api/games/search" # ranked matchmaking vs other AI

# game constants
gameID = '' # id of current game session
playerID = '' # player number
boardSize = -1 # number of units in grid row or column
board = [] # game board (to be re-populated each turn)

#initializes several global constants at gameStart
def setInitialConstants(gameState):
    global gameID, playerID, boardSize
    gameID = gameState['gameID']
    playerID = gameState['playerID']
    boardSize = int(gameState['boardSize'])

# populates a 2d-list of 'Space' objects which contain information about what they contain, as well as whether or not they are in range of an explosion Trail
# todo: currently assumes 0 pierce
def populateBoard(gameState):
    global board
    board = []
    for i in range(boardSize):
        board.append([])
    # first create all spaces
    for i in range(boardSize):
        for r in range(boardSize):
            board[r].append(Space(gameState,r,i,board,boardSize))
    # now check space properties that require an initialized board
    for i in range(boardSize):
        for r in range(boardSize):
            board[r][i].initializeLateProperties(gameState,board,boardSize)

def bisectRightKey(a, x, lo=0, hi=None, key = None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    if key != None:
        x = x.__getattribute__(key)
    while lo < hi:
        mid = (lo+hi)//2
        if key == None:
            value = a[mid]
        else:
            value = a[mid].__getattribute__(key)
        if x < value: hi = mid
        else: lo = mid+1
    return lo

# find shortest path from startSpace to a space satisfying desiredProperty (note: path goes from end to start, not from start to end)
def findPath(startSpace, desiredProperty, desiredState = True, returnAllSolutions = False, allowSoftBlocks = True, destinationCanBeSolidBlock = False,destinationCanBeBomb = False, allowOpponent=True):
    # return a list of all valid adjacent spaces (left, right, up, and down)
    def getAdjacentSpaces(space):
        adjacentSpaces = []
        if (space.x > 0):
            adjacentSpaces.append(board[space.x-1][space.y])
        if (space.y > 0):
            adjacentSpaces.append(board[space.x][space.y-1])
        if (space.x < boardSize - 1):
            adjacentSpaces.append(board[space.x+1][space.y])
        if (space.y < boardSize - 1):
            adjacentSpaces.append(board[space.x][space.y+1])
        return adjacentSpaces

    # are the goal conditions met by this space?
    def conditionMet(space):
        return (True if destinationCanBeSolidBlock else space.type != SpaceType.hardBlock) and \
            (True if destinationCanBeBomb else space.containsBomb == False) and \
            (True if allowSoftBlocks else space.type != SpaceType.softBlock) and \
            (True if allowOpponent else space.containsOpponent == False) and \
            (getattr(space,desiredProperty) == (True if desiredState else False))

    # if startSpace meets the desired property, return it without doing any further calculations
    if (conditionMet(startSpace)):
        if (not returnAllSolutions):
            return [startSpace]
        return [[startSpace]]

    # initialize starting variables
    startSpace.startDistance = 0
    startSpace.parents = []
    closedSet = []
    solutions = []
    finalPathDistance = -1
    openSet = [startSpace]

    # main iteration: keep popping spaces from the back until we have found a solution (or all equal solutions if returnAllSolutions is True) or openSet is empty (in which case there is no solution)
    while (len(openSet) > 0):
        currentSpace = openSet.pop()
        closedSet.append(currentSpace)
        adjacentSpaces = getAdjacentSpaces(currentSpace)

        # main inner iteration: check each space in adjacentSpaces for validity
        for newSpace in adjacentSpaces:
            # if returnAllSolutions is True and we have surpassed finalPathDistance, exit immediately
            if ((finalPathDistance != -1) and (currentSpace.startDistance + 1 > finalPathDistance)):
                return solutions

            # if the newSpace is a goal, find a path back to startSpace (or all equal paths if returnAllSolutions is True)
            if conditionMet(newSpace):
                newSpace.parents = [currentSpace] # start the path with currentSpace and work our way back
                pathsFound = [[newSpace]]

                # grow out the list of paths back in pathsFound until all valid paths have been exhausted
                while (len(pathsFound) > 0):
                    if (pathsFound[0][len(pathsFound[0])-1].parents[0] == startSpace): # we've reached the start space, thus completing this path
                        if (not returnAllSolutions):
                            return pathsFound[0]
                        finalPathDistance = len(pathsFound[0])
                        solutions.append(pathsFound.pop(0))
                        continue

                    # branch additional paths for each parent of the current path's current space
                    for i in range(len(pathsFound[0][len(pathsFound[0])-1].parents)):
                        if (i == len(pathsFound[0][len(pathsFound[0])-1].parents) - 1):
                            pathsFound[0].append(pathsFound[0][len(pathsFound[0])-1].parents[i])
                        else:
                            pathsFound.append(list(pathsFound[0]))
                            pathsFound[len(pathsFound)-1].append(pathsFound[0][len(pathsFound[0])-1].parents[i])

            # attempt to keep branching from newSpace as long as it is a walkable type
            # todo: adjust weighting when encountering soft blocks, as blowing them up will take multiple turns
            if (allowOpponent or newSpace.containsOpponent == False) and (newSpace.containsBomb == False) and \
            (((newSpace.type in (SpaceType.empty, SpaceType.softBlock)) and allowSoftBlocks) or newSpace.type == SpaceType.empty): #sometimes (eg. escaping upcoming trail) we don't want softBlocks in our path
                newStartDistance = currentSpace.startDistance + (10 if newSpace.type == SpaceType.softBlock else 1) #weigh soft blocks as taking 10 moves, as they need to be blown up todo: 10 is a temp value!
                notInOpenSet = not (newSpace in openSet)

                # don't bother with newSpace if it has already been visited unless our new distance from the start space is smaller than its existing startDistance
                if ((newSpace in closedSet) and (newSpace.startDistance < newStartDistance)):
                    continue

                # accept newSpace if newSpace has not yet been visited or its new distance from the start space is equal to its existing startDistance
                if (notInOpenSet or newSpace.startDistance == newStartDistance):
                    if (notInOpenSet): # only reset parent list if this is the first time we are visiting newSpace
                        newSpace.parents = []

                    newSpace.parents.append(currentSpace)
                    newSpace.startDistance = newStartDistance
                    if (notInOpenSet): # if newSpace does not yet exist in the open set, insert it into the appropriate position using a binary search
                        openSet = openSet[::-1] # todo: replace bisectRight with bisectLeft and then delete these reversals
                        openSet.insert(bisectRightKey(openSet,newSpace,key="startDistance"),newSpace)
                        openSet = openSet[::-1]

    if (len(solutions) == 0):
        return None # if solutions is None then that means that no path was found to a space satisfying desiredProperty with desiredState
    return solutions

# return the correct move name to instruct our player to move to the desired space
def moveTo(gameState,space):
    if (space.x > int(gameState['player']['x'])):
        return "mr"
    if (space.x < int(gameState['player']['x'])):
        return "ml"
    if (space.y > int(gameState['player']['y'])):
        return "md"
    if (space.y < int(gameState['player']['y'])):
        return "mu"
    return '' # if space is not adjacent to the player in one of the four cardinal directions, we cannot move to it

# called once per frame. re-populates board, then calls submethods to determine move choice
def chooseMove(gameState):
    # returns a command to move to the next space if we are in danger of an explosion Trail, or None if we are safe
    def escapeTrail():
        # if we are not currently on a space that is slated to contain a trail, we don't need to do anything
        if (not board[int(gameState['player']['x'])][int(gameState['player']['y'])].containsUpcomingTrail):
            return None
        escapePath = findPath(board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsUpcomingTrail",False,allowSoftBlocks=False,allowOpponent=False)
        print("escape path: ",end='')
        print(escapePath)
        print("next block is " + str(escapePath[-1]))
        if (escapePath == None): # todo: we should probably do something here even though we couldn't find a path to escape
            return ''
        if (not escapePath[-1].containsTrail):
            if (escapePath[-1].type == SpaceType.softBlock):
                # todo: we should probably do something here even though the next space in our path is currently a soft block
                return ''
            return moveTo(gameState,escapePath[-1])
        else:
            # todo: we should probably do something here even though the next space in our path is currently lethal
            return ''
        # (old note): perform some basic pathfinding here to get to the closest space where checkConttainsUpcomingTrail is False

    # returns a command to move to the next space in order to approach the opponent, or a bomb command if in range to hit opponent
    def approachOpponent():
        approachPath = findPath(board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsOpponent")
        print("approach path: ",end='')
        print(approachPath)
        print("next block is " + str(approachPath[-1]))
        if (approachPath == None): # todo: we should probably do something here even though we couldn't find a path to approach (this state may be unreachable though depending on implementation)
            return ''
        if (not (approachPath[-1].containsTrail or approachPath[-1].containsUpcomingTrail)): #don't approach into a trail OR an upcoming trail todo: check number of ticks on upcoming trail instead
            if (approachPath[-1].type == SpaceType.softBlock or approachPath[-1].containsOpponent): # place a bomb if we are right next to a soft block or the opponent
                return "b" # todo: this assumes that we currently have a bomb available. Account for case when we do not have any bombs available to use
                return ''
            return moveTo(gameState,approachPath[-1])
        else:
        # todo: we should probably do something here even though the next space in our path is currently lethal
            return ''
        # (old note): perform some basic pathfinding here to get to the shortest path to the opponent (where blocks add a large, temp constant (eg. 15))
    populateBoard(gameState)
    move = escapeTrail()
    return move if move != None else approachOpponent()

def startGame(jsonData):
    print("json data: ",end='')
    print(jsonData)
    setInitialConstants(jsonData)
    print("gameID: " + gameID)
    print("playerID: " + playerID)

#print ascii art representation of the board
def printBoard():
    for i in range(boardSize):
        for j in range(boardSize):
            print(board[j][i].getState(),end=" ")
        print()

def main():
    gameMode = input("Enter 0 for json file, 1 for qualifier bot, 2 for ranked MM, anything else to abort: ").strip()
    if (not (gameMode in ("0","1","2"))):
        raise Exception("Error: Invalid Game Mode.")

    #special mode: generate a single move by reading gameState from JSON file
    if (gameMode == "0"):
        if (not os.path.isfile("gameState.txt")): #verify that the gameState file actually exists before trying to open it
            raise Exception("Error: game state file 'gameState.txt' does not exist.")
        with open('gameState.txt') as infile: 
            jsonData = json.load(infile)
        startGame(jsonData)
        moveChoice = chooseMove(jsonData)
        printBoard()
        print("move choice: " + moveChoice)
        return
        
    r = requests.post(qualifierURL if gameMode == "1" else rankedURL, data={'devkey': devkey, 'username': username}) # search for new game
    jsonData = r.json() # when request comes back, that means you've found a match! (validation if server goes down?)
    startGame(jsonData)
    output = {'state': 'in progress'}
    while output['state'] != 'complete':
        if (debugMode): #when debug mode is enabled, we output the current game state to gameState.txt each turn
            with open('gameState.txt', 'w') as outfile:
                json.dump(jsonData, outfile)
        moveChoice = chooseMove(jsonData)
        printBoard()
        print("move choice: " + moveChoice)
        r = requests.post('http://aicomp.io/api/games/submit/' + gameID, data={'playerID': playerID, 'move': moveChoice, 'devkey': devkey}) # submit sample move
        jsonData = r.json()
        print("json data: ",end='')
        print(jsonData)
        output = jsonData

if __name__ == "__main__": # follow python standard practice in case we decide to run the module from somewhere else
    main()
