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

def setInitialConstants(gameState):
    gameID = gameState['gameID']
    playerID = gameState['playerID']
    boardSize = int(gameState['boardSize'])
    
#get a list of all coords that will be hit by the bomb at position x,y
def checkBombAffectedCoords(x,y,bombPierce,bombRange):
    affectedCoords = [(x,y)]
    
    #todo: repeat code for each direction. clean up.
    #check positive x (right) squares
    curX = x
    curPierce = bombPierce
    for _ in range(bombRange):
        curX+=1
        if curX >= 0 and curX < boardSize:
            affectedCoords.append(curX,y)
            if (board[curX][y].type in [SpaceType.softBlock, SpaceType.hardBlock]):
                curPierce -= 1
                if (curPierce < 0):
                    break
     
    #check negative x (left) squares           
    curX = x
    curPierce = bombPierce
    for _ in range(bombRange):
        curX-=1
        if curX >= 0 and curX < boardSize:
            affectedCoords.append(curX,y)
            if (board[curX][y].type in [SpaceType.softBlock, SpaceType.hardBlock]):
                curPierce -= 1
                if (curPierce < 0):
                    break
                
    #check positive y (down) squares           
    curY = y
    curPierce = bombPierce
    for _ in range(bombRange):
        curY+=1
        if curY >= 0 and curY < boardSize:
            affectedCoords.append(x,curY)
            if (board[x][curY].type in [SpaceType.softBlock, SpaceType.hardBlock]):
                curPierce -= 1
                if (curPierce < 0):
                    break
    
    #check negative y (up) squares           
    curY = y
    curPierce = bombPierce
    for _ in range(bombRange):
        curY-=1
        if curY >= 0 and curY < boardSize:
            affectedCoords.append(x,curY)
            if (board[x][curY].type in [SpaceType.softBlock, SpaceType.hardBlock]):
                curPierce -= 1
                if (curPierce < 0):
                    break

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
                if (bombPlayer == playerID):
                    bombPierce = gameState['player'].bombPierce
                    bombRange = gameState['player'].bombRange
                else:
                    bombPierce = gameState['opponent'].bombPierce
                    bombRange = gameState['opponent'].bombRange
                bombAffectedCoords = checkBombAffectedCoords(bombX,bombY,bombPierce,bombRange)
                if ((self.x,self.y) in bombAffectedCoords):
                    return (True,bombTurnsRemaining)
            return (False,-1)
                

#populates a 2d-list of 'Space' objects which contain information about what they contain, as well as whether or not they are in range of an explosion Trail
#todo: currently assumes 0 pierce
def populateBoard(gameState):
    board = [[]*boardSize]
    for i in range(boardSize):
        x = i%boardSize
        y = i//boardSize
        board[x][y] = Space(gameState,x,y)
    return board    

def chooseMove(gameState):
    board = populateBoard(gameState)
    move = escapeTrail()
    return move if move != None else approachOpponent()      
    
    #returns a command to move to the next space if we are in danger of an explosion Trail, or None if we are safe
    def escapeTrail():
        pass
    
    #returns a command to move to the next space in order to approach the opponent, or a bomb command if next to a soft block or 3 spaces from the opponent
    def approachOpponent():
        pass  

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
        r = requests.post('http://aicomp.io/api/games/submit/' + gameID, data={'playerID': playerID, 'move': possibleMoves[moveChoice], 'devkey': devkey}); # submit sample move
        json = r.json()
        print(json)
        output = json

if __name__ == "__main__": #follow python standard practice in case we decide to run the module from somewhere else
    main()
