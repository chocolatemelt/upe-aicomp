'''
Created on Nov 18, 2016

@author: Ryan
'''
from space import Space
from portalUtilities import *
#returns a set of spaces hit by the apocalypse, given n iterations
#@param iters: the number of apocalypse iterations that have occurred (turn <= 400 is 0 iterations)
def apocaSpaces(iters):
    #HELPER FUNCTION FOR THE apocaSpaces FUNCTION
    def opposite(loc):
        (x,y) = loc
        return (10-x, 10-y)
    
    #HELPER FUNCTION FOR THE apocaSpaces FUNCTION
    def makeStep(loc, stepDir):
        (x,y) = loc
        if stepDir == 0:
            y -= 1
        elif stepDir == 1:
            x -= 1
        elif stepDir == 2:
            y += 1
        elif stepDir == 3:
            x += 1
        else:
            print("invalid stepDirection input: " + str(stepDir))
        return (x,y)
    
    invalid = set()
    if iters == 0:
        return invalid
    #the bottom left's initial location
    location = (10,0)
    #bottom left's initial direction (north)
    direction = 1
    
    #iterate iters times
    for _ in range(iters):
        #add the invalid location and its opposite block
        invalid.add(location)
        invalid.add(opposite(location))
        newloc = makeStep(location, direction)
        (x,y) = newloc
        # if we've stepped out of bounds, change direction and make new step
        # or if we've looped back
        if newloc in invalid or x == -1 or x == 11 or y == -1 or y == 11:
            direction = (direction + 1) % 4
            newloc = makeStep(location, direction)
        #print(direction)
        location = newloc
    return invalid

def applyMove(board,gameState, move, player = "player"):
    """make the appropriate changes to board and gameState in order to apply move for selected player"""
    pass

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

def calculateBlockPlacementCost(boardSize, desiredSpace):
    """determine the coin cost to purchase a block placement at the selected position.
    Note: placement cost has a minimum of 1!"""
    return min(((boardSize - 1 - desiredSpace.x) * desiredSpace.x * (boardSize - 1 - desiredSpace.y) * desiredSpace.y * 10 / ((boardSize - 1)**4 / 16))//2,1) 

def copyGame(board,gameState):
    """generate and return a deep copy of board and gameState"""
    return unshared_copy(board),gameState.deepcopy()

def findPath(gameState,board,startSpace, desiredProperty, desiredState = True, returnAllSolutions = False, allowSoftBlocks = True, destinationCanBeSolidBlock = False,
             destinationCanBeBomb = False, allowOpponent=True,softBlockWeight=10):
    """find shortest path from startSpace to a space satisfying desiredProperty (note: path goes from end to start, not from start to end)"""
    #todo: this will recognize the existence of portals, but makes no attempt to place portals as part of the pathfinding
    def conditionMet(space):
        """are the goal conditions met by this space?"""
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
        adjacentSpaces = getAdjacentSpaces(board,currentSpace)

        # main inner iteration: check each space in adjacentSpaces for validity
        for newSpace in adjacentSpaces:
            # if returnAllSolutions is True and we have surpassed finalPathDistance, exit immediately
            if ((finalPathDistance != -1) and (currentSpace.startDistance + 1 > finalPathDistance)):
                return solutions
            
            canTraverse = canTraversePortal(board,gameState,currentSpace,newSpace)
            if (canTraverse[0]): #if the current block is a wall with a portal on it, re-assign it to the destination block 
                newSpace = canTraverse[1] 

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
            if (allowOpponent or newSpace.containsOpponent == False) and (newSpace.containsBomb == False) and \
            (((newSpace.type in (SpaceType.empty, SpaceType.softBlock)) and allowSoftBlocks) or newSpace.type == SpaceType.empty): #sometimes (eg. escaping upcoming trail) we don't want softBlocks in our path
                newStartDistance = currentSpace.startDistance + (softBlockWeight if newSpace.type == SpaceType.softBlock else 1) #weigh soft blocks as taking 10 moves, as they need to be blown up todo: 10 is a temp value!
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

def findPortalBlock(board,startSpace,direction):
    """find the block that a fired portal will land on starting at startSpace and traveling in direction"""
    curSpace = startSpace
    while (not (curSpace.type == SpaceType.softBlock or curSpace.type == SpaceType.hardBlock)): #here we assume that the boad is surrounded by walls (ie. this cannot infinite loop)
        curSpace = getAdjacentSpaces(board,curSpace,direction)
    return curSpace

def moveTo(gameState,board,space,player = "player"):
    """return the correct move name to instruct our player to move to the desired space"""
    if (space.x - int(gameState[player]['x']) == 1):
        return "mr"
    if (space.x - int(gameState[player]['x']) == -1):
        return "ml"
    if (space.y - int(gameState[player]['y']) == 1):
        return "md"
    if (space.y - int(gameState[player]['y']) == -1):
        return "mu"
    #check if moving to the space can be achieved by using a portal
    boardSize = len(board)
    playerX = int(gameState[player]['x'])
    playerY = int(gameState[player]['y'])
    if (playerX < boardSize - 1):
        dest = canTraversePortal(board,gameState,board[playerX][playerY],board[playerX+1][playerY])
        if dest[1] == space:
            return "mr"
    if (playerX > 0):
        dest = canTraversePortal(board,gameState,board[playerX][playerY],board[playerX-1][playerY])
        if dest[1] == space:
            return "ml"
    if (playerY < boardSize - 1):
        dest = canTraversePortal(board,gameState,board[playerX][playerY],board[playerX][playerY+1])
        if dest[1] == space:
            return "md"
    if (playerY > 0):
        dest = canTraversePortal(board,gameState,board[playerX][playerY],board[playerX][playerY-1])
        if dest[1] == space:
            return "mu"
    return '' # if space is not adjacent to the player in one of the four cardinal directions, we cannot move to it

def moveValid(board,gameState, move,player = "player"):
    """determine if the given move is valid for the selected player given the board and gameState.
    Note: moves that are valid but will not affect the gameState in any way return False!"""
    if move == (''):
        return True
    if (move in ("ml","mu","mr","md")):
        #translate move command to direction string, and feed that into getAdjacentSpaces
        space = getAdjacentSpaces(board, board[int(gameState[player]['x'])][int(gameState[player]['y'])], ("left","up","right","down")[("ml","mu","mr","md").index(move)])
        return space != None and space.type == SpaceType.empty
    if (move in ("tl","tu","tr","td")):
        #disallow turning to the current facing direction (directions: left = 0, up = 1, right = 2, down = 3)
        return ("tl","tu","tr","td")[int(gameState[player]["orientation"])] != move
    if (move == "b"):
        #make sure the selected player has a bomb and is not currently sitting on top of a bomb
        return int(gameState[player]["bombCount"]) > 0 and board[int(gameState[player]['x'])][int(gameState[player]['y'])].containsBomb == False
    if (move in ('buy_count', 'buy_range', 'buy_pierce')):
        #make sure the selected player has enough money to purchase the selected upgrade
        return gameState[player]["coins"] >= 5
    if (move == "op" or move == "bp"):
        #verify that the block that this portal will land on does not already contain the same colored portal from this player 
        portalBlock = findPortalBlock(board,board[int(gameState[player]['x'])][int(gameState[player]['y'])],("left","up","right","down")[int(gameState[player]["orientation"])])
        if gameState[player]["orangePortal" if move == "op" else "bluePortal"] == None: #if the portal is not yet placed, we guarantee that we are not overriding it
            return True
        return not (int(gameState[player]["orangePortal" if move == "op" else "bluePortal"]["x"]) == portalBlock.x and int(gameState[player]["orangePortal" if move == "op" else "bluePortal"]["y"]) == portalBlock.y)
        
    if (move == "buy_block"):
        #determine the selected player's facing space, and then make sure the player has enough coins to place a block there if the space is empty
        facingSpace = getAdjacentSpaces(board, board[int(gameState[player]['x'])][int(gameState[player]['y'])], ("left","up","right","down")[int(gameState[player]["orientation"])])
        return facingSpace != None and facingSpace.type == SpaceType.empty and gameState[player]["coins"] >= calculateBlockPlacementCost(len(board),facingSpace) 
    
def populateBoard(gameState):
    """populates a 2d-list of 'Space' objects which contain information about what they contain, as well as whether or not they are in range of an explosion Trail"""
    boardSize = int(gameState['boardSize']) # number of units in grid row or column
    board = []
    for i in range(boardSize):
        board.append([])
    # first create all spaces
    for i in range(boardSize):
        for r in range(boardSize):
            board[r].append(Space(gameState,r,i,board))
    # now check space properties that require an initialized board
    for i in range(boardSize):
        for r in range(boardSize):
            board[r][i].initializeLateProperties(gameState,board)
    return board

def printBoard(board):
    """print ascii art representation of the 2D list of Spaces board"""
    for i in range(len(board)):
        for j in range(len(board)):
            print(board[j][i].getState(),end=" ")
        print()

def selectGameMode():
    """request game mode as input. Raises Exception for invalid mode selection"""
    gameMode = input("Enter 0 for json file, 1 for qualifier bot, 2 for ranked MM, anything else to abort: ").strip()
    if (not (gameMode in ("0","1","2"))):
        raise Exception("Error: Invalid Game Mode.")
    return gameMode

def startGame(jsonData):
    """set constants at game start and print some data"""
    gameID,playerID = (jsonData['gameID'],jsonData['playerID']) # store id of current game session, and player number
    print("json data:",jsonData)
    print("gameID: {0}\nplayerID: {1}".format(gameID, playerID))
    return gameID,playerID

def unshared_copy(inList):
    """perform a proper deepcopy of a multi-dimensional list (function from http://stackoverflow.com/a/1601774)"""
    if isinstance(inList, list):
        return list( map(unshared_copy, inList) )
    return inList

def main():
    #if we're running this helper class directly, perform some unit tests
    print(apocaSpaces(400))

if __name__ == "__main__":
    main()