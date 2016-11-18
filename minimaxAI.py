"""basic AI designed to overcome basic, common circumstances in order to beat random the qualifier bot"""
import requests #needed to send and receive data from the server
import json #allows us to test the game at a single point in time by reading / writing JSON data to a file
import os.path #allows us to check if JSON file exists before attempting to read data from it when in debug mode
from space import Space, SpaceType #custom space class containing information about a given board position
import utilities as util#several misc functions that are unrelated to functionality or not specific to AI

debugMode = True #flag which instructs the program to write gameState to JSON file each turn for future processing

# initialize global networking constants
username = "kzhaaang"
devkey = "5823b8c404d7ce4a44c37ab4"
qualifierURL = "http://aicomp.io/api/games/practice" # practice qualifier bot
rankedURL = "http://aicomp.io/api/games/search" # ranked matchmaking vs other AI

# declare global game constants
gameID = '' # id of current game session
playerID = '' # player number
boardSize = -1 # number of units in grid row or column

def setInitialConstants(gameState):
    """initialize global constants at gameStart"""
    global gameID, playerID, boardSize
    gameID = gameState['gameID']
    playerID = gameState['playerID']
    boardSize = int(gameState['boardSize'])

def chooseMove(board,gameState):
    """called once per frame. re-populates board, then calls submethods to determine move choice"""
    def escapeTrail():
        """returns a command to move to the next space if we are in danger of an explosion Trail, or None if we are safe"""
        # if we are not currently on a space that is slated to contain a trail, we don't need to do anything
        if (not board[int(gameState['player']['x'])][int(gameState['player']['y'])].containsUpcomingTrail):
            return None
        escapePath = util.findPath(board,board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsUpcomingTrail",False,allowSoftBlocks=False,allowOpponent=False)
        print("escape path: {0}\nnext block is: {1}".format(escapePath,escapePath[-1]))
        if (escapePath == None): # todo: we should probably do something here even though we couldn't find a path to escape
            return ''
        if (not escapePath[-1].containsTrail):
            if (escapePath[-1].type == SpaceType.softBlock):
                # todo: we should probably do something here even though the next space in our path is currently a soft block
                return ''
            return util.moveTo(gameState,escapePath[-1])
        else:
            # todo: we should probably do something here even though the next space in our path is currently lethal
            return ''

    def approachOpponent():
        """returns a command to move to the next space in order to approach the opponent, or a bomb command if in range to hit opponent"""
        approachPath = util.findPath(board,board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsOpponent")
        print("escape path: {0}\nnext block is: {1}".format(approachPath,approachPath[-1]))
        if (approachPath == None): # todo: we should probably do something here even though we couldn't find a path to approach (this state may be unreachable though depending on implementation)
            return ''
        if (not (approachPath[-1].containsTrail or approachPath[-1].containsUpcomingTrail)): #don't approach into a trail OR an upcoming trail todo: check number of ticks on upcoming trail instead
            if (approachPath[-1].type == SpaceType.softBlock or approachPath[-1].containsOpponent): # place a bomb if we are right next to a soft block or the opponent
                return "b" # todo: this assumes that we currently have a bomb available. Account for case when we do not have any bombs available to use
                return ''
            return util.moveTo(gameState,approachPath[-1])
        else:
        # todo: we should probably do something here even though the next space in our path is currently lethal
            return ''
        
    move = escapeTrail()
    return move if move != None else approachOpponent()

def startGame(jsonData):
    """set constants at game start and print some data"""
    setInitialConstants(jsonData)
    if (debugMode):
        print("json data:",jsonData)
        print("gameID: {0}\nplayerID: {1}".format(gameID, playerID))

def main():
    gameMode = util.selectGameMode()
    #special mode: generate a single move by reading gameState from JSON file
    if (gameMode == "0"):
        if (not os.path.isfile("gameState.txt")): #verify that the gameState file actually exists before trying to open it
            raise Exception("Error: game state file 'gameState.txt' does not exist.")
        with open('gameState.txt') as infile: #load game state from gameState.txt
            jsonData = json.load(infile)
        startGame(jsonData)
        board = util.populateBoard(jsonData)
        util.printBoard(board)
        moveChoice = chooseMove(board,jsonData)
        print("move choice:", moveChoice)
        return
        
    jsonData = requests.post(qualifierURL if gameMode == "1" else rankedURL, data={'devkey': devkey, 'username': username}).json() # search for new game
    # when request comes back, that means you've found a match! (validation if server goes down?)
    startGame(jsonData)
    while jsonData['state'] != 'complete':
        if (debugMode): #when debug mode is enabled, we output the current game state to gameState.txt each turn
            with open('gameState.txt', 'w') as outfile:
                json.dump(jsonData, outfile)
        board = util.populateBoard(jsonData)
        util.printBoard(board)
        moveChoice = chooseMove(board,jsonData)
        print("move choice:", moveChoice)
        jsonData = requests.post('http://aicomp.io/api/games/submit/' + gameID, data={'playerID': playerID, 'move': moveChoice, 'devkey': devkey}).json() # submit sample move
        print("json data:", jsonData)

if __name__ == "__main__": # follow python standard practice in case we decide to run the module from somewhere else
    main()