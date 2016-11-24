"""AI designed to make intelligent move selections based on future gameStates using minimax tree"""
from space import Space, SpaceType #custom space class containing information about a given board position
import utilities as util#several misc functions that are unrelated to functionality or not specific to AI
possibleMoves = ['mu', 'ml', 'mr', 'md', 'tu', 'tl', 'tr', 'td', 'b', '', 'op', 'bp', 'buy_count', 'buy_range', 'buy_pierce', 'buy_block']  #full list of moves (copied from sampleAI)
numFutureTurns = 3 #how many turns into the future should the minimaxAI search

def chooseMove(board,gameState): # todo: put move selection logic here
    """called each turn. generates tree of potential future gameStates, then selects the Node leading to the least loss"""
    def calculateScore(board,gameState):
        """generate a score for the given board and gameState"""
        pass
    
    def findOptimalMove(curBoard,curGameState,curTurn = 0):
        """find the highest score move from curTurn to numFutureTurns"""
        #first determine if each possible move is valid (will affect game in some way)
        possibleMovesValid = [util.moveValid(board, gameState, move, 'player') for move in possibleMoves]
        validMoves = []
        for i in range(len(possibleMovesValid)):
            if (possibleMovesValid[i]):
                validMoves.append(possibleMoves[i])
                
        #display some debug info
        print("possibleMoves:     ",possibleMoves)
        print("possibleMovesValid:",possibleMovesValid)
        print("validMoves:        ",validMoves)
        
        #attempt to execute each move on a separate copy of the board and gameData
        for move in validMoves:
            newBoard,newGameState = util.copyGame(curBoard,curGameState)
            util.applyMove(newBoard, newGameState, move, 'player')
            
        
    return findOptimalMove(board,gameState)