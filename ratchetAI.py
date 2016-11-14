"""basic AI designed to overcome basic, common circumstances in order to beat random the qualifier bot"""
import requests
from enum import Enum

#networking constants
username = "kzhaaang"
devkey = "5823b8c404d7ce4a44c37ab4"
qualifierURL = "http://aicomp.io/api/games/practice" #practice qualifier bot
rankedURL = "http://aicomp.io/api/games/search" #ranked matchmaking vs other AI

#game constants
gameID = '' #id of current game session
playerID = '' #player number
boardSize = -1 #number of units in grid row or column
board = [[]*boardSize] #game board (to be re-populated each turn)

#Enum of valid space types
SpaceType = Enum("SpaceType", "empty softBlock hardBlock")

#basic class containing info on a single unit space, including what that space is, and whether or not it is in range of an upcoming or active explosion Trail
class Space():
    def __init__(self,gameState,x,y):
        self.x = x
        self.y = y
        self.type = checkType()
        self.containsBomb = checkContainsBomb()
        self.containsTrail = checkContainsTrail()
        #todo: may be thrown off if bomb range and pierce count are upgraded after placing (depending on game mechanics)
        self.containsUpcomingTrail,self.turnsUntilUpcomingTrail = checkContainsUpcomingTrail()
        self.containsPlayer,self.containsOpponent = checkContainsEitherPlayer()
        
        #set whether or not the player or the opponent is currently on this space
        def checkContainsEitherPlayer():
            return int(gameState['player']['x']) == self.x and int(gameState['player']['y']) == self.y, int(gameState['opponent']['x']) == self.x and int(gameState['opponent']['y']) == self.y
        
        #set type according to gameState
        def checkType():
            if (int(gameState['hardBlockBoard'][self.y*boardSize + self.x]) == 1):
                return SpaceType.empty
            if (int(gameState['softBlockBoard'][self.y*boardSize + self.x]) == 1):
                return SpaceType.softBlock
            return SpaceType.hardBlock
        
        #set whether or not a bomb is currently on this space
        def checkContainsBomb():
            bombKeys = gameState['bombMap'].keys()
            for coord in bombKeys:
                bombX = int(coord.split(",")[0])
                bombY = int(coord.split(",")[1])
                if (bombX ==self.x and bombY == self.y):
                    return True
            return False
        
        #set whether or not an explosion Trail is currently on this space
        def checkContainsTrail():
            trailKeys = gameState['trailMap'].keys()
            for coord in trailKeys:
                trailX = int(coord.split(",")[0])
                trailY = int(coord.split(",")[1])
                if (trailX ==self.x and trailY == self.y):
                    return True
            return False
        
        #set whether or not an explosion Trail will soon be on this space
        def checkContainsUpcomingTrail():
            #todo: repeat code from checkContainsBomb
            bombKeys = gameState['bombMap'].keys()
            for coord in bombKeys:
                bombX = int(coord.split(",")[0])
                bombY = int(coord.split(",")[1])
                bombPlayer = gameState['bombMap'][coord]['owner']
                bombTurnsRemaining = gameState['bombMap'][coord]['tick']
                if (bombPlayer == gameState['playerIndex']):
                    bombPierce = gameState['player'].bombPierce
                    bombRange = gameState['player'].bombRange
                else:
                    bombPierce = gameState['opponent'].bombPierce
                    bombRange = gameState['opponent'].bombRange
                bombAffectedCoords = checkBombAffectedCoords(bombX,bombY,bombPierce,bombRange)
                if ((self.x,self.y) in bombAffectedCoords):
                    return (True,bombTurnsRemaining)
            return (False,-1)
   
def setInitialConstants(gameState):
    global gameID, playerID
    gameID = gameState['gameID']
    playerID = gameState['playerID']
    boardSize = int(gameState['boardSize'])
    
#get a list of all coords that will be hit by the bomb at position x,y
def checkBombAffectedCoords(x,y,bombPierce,bombRange):
    affectedCoords = [(x,y)] # the bomb square itself will be hit no matter what
    #check negative x (left) then positive x (right) squares, then negative y (up) and then finally positive y (down) squares
    for direction in range(-1, 6, 2):
        curPierce = bombPierce
        curX = x, curY = y
        for _ in range(bombRange):
            if (direction <= 1):
                curX += direction
            else:
                curY += direction-4 #offset of 4 so that -1 -> 1 account for x increments, and 3 -> 5 (minus 4) account for y increments
            if curX >= 0 and curX < boardSize and curY >= 0 and curY < boardSize:
                affectedCoords.append(curX,curY)
                if (board[curX][curY].type in [SpaceType.softBlock, SpaceType.hardBlock]):
                    curPierce -= 1
                    if (curPierce < 0):
                        break   
    return affectedCoords      

#populates a 2d-list of 'Space' objects which contain information about what they contain, as well as whether or not they are in range of an explosion Trail
#todo: currently assumes 0 pierce
def populateBoard(gameState):
    board = [[]*boardSize]
    for i in range(boardSize):
        x = i%boardSize
        y = i//boardSize
        board[x][y] = Space(gameState,x,y)
    return board    

def binarySearch(a, x, key, leftMost = False, lo = 0, hi = None):
    """Return the index where to insert item x in list a, assuming a is sorted.
    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched."""
    if (hi == None):
        hi = a.length
    if (key != None):
        x = eval("x." + key) 
    
    if (leftMost):
        while (lo < hi):
            mid = (lo+hi)//2
            if (key == None):
                value = a[mid]
            else:
                value = eval("a[mid]." + key)
            
            if (x <= value):
                hi = mid
            else:
                lo = mid+1
                
    else:
        while (lo < hi):
            mid = (lo+hi)//2
            if (key == None):
                value = a[mid]
            else:
                value = eval("a[mid]." + key)
            
            if (x < value):
                hi = mid
            else:
                lo = mid+1

    return lo

#find shortest path from startSpace to a space satisfying desiredProperty
def findPath(startSpace, desiredProperty, desiredState = True, returnAllSolutions = False):
    if (conditionMet(startSpace)): #if startSpace meets the desired property, return it without doing any further calculations
        if (not returnAllSolutions):
            return [startSpace]
        return [[startSpace]]
    
    #initialize variables
    startSpace.startDistance = 0
    startSpace.parents = []
    closedSet = []
    solutions = []
    finalPathDistance = -1
    openSet = [startSpace]
    
    #main iteration: keep popping spaces from the back until we have found a solution (or all equal solutions if returnAllSolutions is True) or openSet is empty (in which case there is no solution)
    while (len(openSet) > 0):
        currentSpace = openSet.pop()
        closedSet.append(currentSpace)
        adjacentSpaces = getAdjacentSpaces(currentSpace)
        
        #main inner iteration: check each space in adjacentSpaces for validity
        for newSpace in adjacentSpaces:
            #if returnAllSolutions is True and we have surpassed finalPathDistance, check if current solution is less optimal, in which case exit immediately
            if ((finalPathDistance != -1) and (currentSpace.startDistance + 1 > finalPathDistance)):
                return solutions
            
            #if the newSpace is a goal, find a path back to startSpace (or all equal paths if returnAllSolutions is True) 
            if conditionMet(newSpace):
                newSpace.parents = [currentSpace] #start the path with currentSpace and work our way back
                pathsFound = [[newSpace]]
                
                #grow out the list of paths back in pathsFound until all valid paths have been exhausted
                while (len(pathsFound) > 0): 
                    if (pathsFound[0][len(pathsFound[0])-1].parents[0] == startSpace): #we've reached the start space, thus completing this path
                        if (not returnAllSolutions):
                            return pathsFound[0]
                        finalPathDistance = len(pathsFound[0])
                        solutions.append(pathsFound.pop(0))
                        continue
                    
                    #branch additional paths for each parent of the current path's current space
                    for i in range(len(pathsFound[0][len(pathsFound[0])-1].parents)):
                        if (i == len(pathsFound[0][len(pathsFound[0])-1].parents) - 1):
                            pathsFound[0].append(pathsFound[0][len(pathsFound[0])-1].parents[i])
                        else:
                            pathsFound.push(list(pathsFound[0]))
                            pathsFound[len(pathsFound)-1].push(pathsFound[0][len(pathsFound[0])-1].parents[i])
                            
            #attempt to keep branching from newSpace as long as it is a walkable type
            #todo: adjust weighting when encountering soft blocks, as blowing them up will take multiple turns
            if ((newSpace.type in [SpaceType.empty, SpaceType.softBlock])):                    
                newStartDistance = currentSpace.startDistance + 1
                notInOpenSet = not newSpace in openSet
                
                #don't bother with newSpace if it has already been visited unless our new distance from the start space is smaller than its existing startDistance
                if ((newSpace in closedSet) and (newSpace.startDistance < newStartDistance)):
                    continue
                
                #accept newSpace if newSpace has not yet been visited or its new distance from the start space is equal to its existing startDistance
                if (notInOpenSet or newSpace.startDistance == newStartDistance):
                    if (notInOpenSet): #only reset parent list if this is the first time we are visiting newSpace
                        newSpace.parents = []
                    
                    newSpace.parents.push(currentSpace)
                    newSpace.startDistance = newStartDistance
                    if (notInOpenSet): #if newSpace does not yet exist in the open set, insert it into the appropriate position using a binary search
                        openSet.insert(binarySearch(openSet,newSpace,"startDistance",True),newSpace)
                
    if (len(solutions) == 0):
        return None #if solutions is None then that means that no path was found to a space satisfying desiredProperty
    return solutions                  
    
    #return a list of all valid adjacent spaces (left, right, up, and down) 
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
    
    #are the goal conditions met by this space?
    def conditionMet(space):
        return eval("space."+desiredProperty+"== (True if desiredState else False)")

#return the correct move name to instruct our player to move to the desired space
def moveTo(gameState,space):
    if (space.x > int(gameState['player'].x)):
        return "mr"
    if (space.x < int(gameState['player'].x)):
        return "ml"
    if (space.y > int(gameState['player'].y)):
        return "md"
    if (space.y < int(gameState['player'].y)):
        return "mu"
    return '' #if space is not adjacent to the player in one of the four cardinal directions, we cannot move to it
    
#called once per frame. re-populates board, then calls submethods to determine move choice
def chooseMove(gameState):
    board = populateBoard(gameState)
    move = escapeTrail()
    return move if move != None else approachOpponent()      
    
    #returns a command to move to the next space if we are in danger of an explosion Trail, or None if we are safe
    def escapeTrail():
        #if we are not currently on a space that is slated to contain a trail, we don't need to do anything
        if (not board[int(gameState['player'].x)][int(gameState['player'].y)].containsUpcomingTrail):
            return None
        escapePath = findPath(board[int(gameState['player'].x)][int(gameState['player'].y)],"containsUpcomingTrail",False)
        if (escapePath == None): #todo: we should probably do something here even though we couldn't find a path to escape
            return ''
        if (not escapePath[0].containsTrail):
            if (escapePath[0].type == SpaceType.softBlock):
                #todo: we should probably do something here even though the next space in our path is currently a soft block
                return ''
            return moveTo(gameState,escapePath[0])
        else: 
            #todo: we should probably do something here even though the next space in our path is currently lethal
            return ''
        #todo: perform some basic pathfinding here to get to the closest space where checkConttainsUpcomingTrail is False
    
    #returns a command to move to the next space in order to approach the opponent, or a bomb command if in range to hit opponent
    def approachOpponent():
        approachPath = findPath(board[int(gameState['player'].x)][int(gameState['player'].y)],"containsOpponent")
        if (approachPath == None): #todo: we should probably do something here even though we couldn't find a path to approach (this state may be unreachable though depending on implementatino)
            return ''
        if (not approachPath[0].containsTrail):
            if (approachPath[0].type == SpaceType.softBlock):
                return "b" #todo: this assumes that we currently have a bomb available. Account for case when we do not have any bombs available to use
                return ''
            return moveTo(gameState,approachPath[0])
        else: 
            #todo: we should probably do something here even though the next space in our path is currently lethal
            return ''
        #todo: perform some basic pathfinding here to get to the shortest path to the opponent (where blocks add a large, temp constant (eg. 15))

def main():
    gameMode = input("Enter 1 for qualifier bot, 2 for ranked MM, anything else to abort: ").strip()
    if (not (gameMode == "1" or gameMode == "2")):
        raise Exception("Error: Invalid Game Mode. Aborting.")

    r = requests.post(qualifierURL if gameMode == "1" else rankedURL, data={'devkey': devkey, 'username': username}) # search for new game
    json = r.json() # when request comes back, that means you've found a match! (validation if server goes down?)
    print(json)
    
    setInitialConstants(json)

    print(gameID)
    print(playerID)
    possibleMoves = ['mu', 'ml', 'mr', 'md', 'tu', 'tl', 'tr', 'td', 'b', '', 'op', 'bp', 'buy_count', 'buy_range', 'buy_pierce', 'buy_block']
    output = {'state': 'in progress'}
    while output['state'] != 'complete':
        moveChoice = chooseMove(json) #todo: we should actually calculate a move here based on board / game state
        r = requests.post('http://aicomp.io/api/games/submit/' + gameID, data={'playerID': playerID, 'move': possibleMoves[moveChoice], 'devkey': devkey}) # submit sample move
        json = r.json()
        print(json)
        output = json

if __name__ == "__main__": #follow python standard practice in case we decide to run the module from somewhere else
    main()
