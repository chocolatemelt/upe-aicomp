"""basic AI designed to overcome basic, common circumstances in order to beat random the qualifier bot"""
import requests #needed to send and receive data from the server
import json #allows us to test the game at a single point in time by reading / writing JSON data to a file
import os.path #allows us to check if JSON file exists before attempting to read data from it when in debug mode
from space import Space, SpaceType #custom space class containing information about a given board position
import utilities as util#several misc functions that are unrelated to functionality or not specific to AI
import ratchetAI as ratchet #basic AI which operates by approaching the opponent, placing bombs when necessary, and evading bomb trails
import minimaxAI as minimax #smarter AI which operates by generating a tree of future gameStates, and selecting the Node which leads to the least loss

debugMode = True #flag which instructs the program to write gameState to JSON file each turn for future processing
AIMode = "ratchet"

# initialize global networking constants
username = "kzhaaang"
devkey = "5823b8c404d7ce4a44c37ab4"
qualifierURL = "http://aicomp.io/api/games/practice" # practice qualifier bot
rankedURL = "http://aicomp.io/api/games/search" # ranked matchmaking vs other AI

def main():
    """main function which handles loading up the AI each turn and communicating with the game server"""
    gameMode = util.selectGameMode()
    #special mode: generate a single move by reading gameState from JSON file
    if (gameMode == "0"):
        if (not os.path.isfile("gameState.txt")): #verify that the gameState file actually exists before trying to open it
            raise Exception("Error: game state file 'gameState.txt' does not exist.")
        with open('gameState.txt') as infile: #load game state from gameState.txt
            jsonData = json.load(infile)
        util.startGame(jsonData) #don't bother to store gameID or playerID here, as we are just running locally in mode 0, so we don't need these networking constants
        board = util.populateBoard(jsonData)
        util.printBoard(board)
        moveChoice = eval(AIMode + ".chooseMove(board,jsonData)")
        print("move choice:", moveChoice)
        return

    jsonData = requests.post(qualifierURL if gameMode == "1" else rankedURL, data={'devkey': devkey, 'username': username}).json() # search for new game
    # when request comes back, that means you've found a match! (validation if server goes down?)
    gameID,playerID = util.startGame(jsonData)
    while jsonData['state'] != 'complete':
        if (debugMode): #when debug mode is enabled, we output the current game state to gameState.txt each turn
            with open('gameState.txt', 'w') as outfile:
                json.dump(jsonData, outfile)
        board = util.populateBoard(jsonData)
        util.printBoard(board)
        moveChoice = eval(AIMode + ".chooseMove(board,jsonData)")
        print("move choice:", moveChoice)
        jsonData = requests.post('http://aicomp.io/api/games/submit/' + gameID, data={'playerID': playerID, 'move': moveChoice, 'devkey': devkey}).json() # submit sample move
        print("json data:", jsonData)

if __name__ == "__main__": # follow python standard practice in case we decide to run the module from somewhere else
    main()
