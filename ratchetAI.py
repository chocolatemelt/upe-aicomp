"""basic AI designed to overcome basic, common circumstances in order to beat random the qualifier bot"""
import requests

#networking constants
username = "kzhaaang"
devkey = "5823b8c404d7ce4a44c37ab4"
qualifierURL = "http://aicomp.io/api/games/practice" #practice qualifier bot
rankedURL = "http://aicomp.io/api/games/search" #ranked matchmaking vs other AI

#game constants
gameID = '' #id of current game session
playerID = '' #player number
boardSize = -1 #number of units in grid row or column

def setInitialConstants(gameState):
    gameID = gameState['gameID']
    playerID = gameState['playerID']
    boardSize = gameState['boardSize']

#basic class containing info on a single unit space, including what that space is, and whether or not it is in range of an upcoming or active explosion
class Space():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.type = "empty"
        self.containsExplosion = False
        self.containsUpcomingExplosion = False
    
    def setContainsExplosion(self):
        self.containsExplosion = True
    
    def setContainsUpcomingExplosion(self):
        self.containsUpcomingExplosion = True

#populates a 2d-list of 'Space' objects which contain information about what they contain, as well as whether or not they are in range of an explosion (currently assumes 0 pierce)
def populateBoard(gameState):
    board = []
    

def chooseMove(gameState):
    board = populateBoard(gameState)
    move = inExplosionDanger()
    return move if move != None else approachOpponent()      
    
    #returns a command to move to the next space if we are in danger of an explosion, or None if we are safe
    def inExplosionDanger():
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
