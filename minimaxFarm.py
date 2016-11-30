"""AI designed to make intelligent move selections based on future gameStates using minimax tree"""
from space import Space, SpaceType #custom space class containing information about a given board position
import utilities as util#several misc functions that are unrelated to functionality or not specific to AI
possibleMoves = ['mu', 'ml', 'mr', 'md', 'tu', 'tl', 'tr', 'td', 'b', '', 'op', 'bp', 'buy_count', 'buy_range', 'buy_pierce', 'buy_block']  #full list of moves (copied from sampleAI)
possibleDMoves = ['mu','ml','mr','md']
numFutureTurns = 3 #how many turns into the future should the minimaxAI search

def chooseMove(board,gameState): # todo: put move selection logic here
    """called each turn. generates tree of potential future gameStates, then selects the Node leading to the least loss"""

    FarmPhase = true

    if (gameState['player']['bombPierce'] > 3 and gameState['player']['bomRange'] > 6):
        FarmPhase = false

    # a function that returns a list of coordinates of spots reachable by foot. (maybe within 5 blocks?)
    # a function that returns True/False for if I place a bomb, will it destroy soft-blocks
    # a function that anticipates a trail map of a bomb placement

    # account for downtime, so move if you don't have any bombCount
    # prioritize a concentrated area of blocks?, or alternate placing bombs from two different areas

    if FarmPhase:

        if (gameState['player']['bombCount']) > 0:
        #If I have bombs in bombCount
            if util.goodbombSpot(board,gameState):
            #if I place a bomb where I am standing, will it destroy soft-blocks and can I get out of its way (and the way of other bombs)? 
                return 'b'
            else:
            #if not, move to a location that is safe from existing bombs and where I can place a bomb to destroy soft-blocks
                escapePath = util.findPath(board,board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsUpcomingTrail",False,allowSoftBlocks=False,allowOpponent=False)
                print("escape path: {0}\nnext block is: {1}".format(escapePath,escapePath[-1]))
                if (not escapePath[-1].containsTrail):
                    if (escapePath[-1].type == SpaceType.softBlock):
                        # todo: we should probably do something here even though the next space in our path is currently a soft block
                        return ''
                    return util.moveTo(gameState,escapePath[-1])

                #To-Do: I've moved to a location that is safe from existing bombs, now make stronger constraint where I can place a bomb to destroy soft-blocks

        else:
        #Else, move to a location that is safe from existing bombs and where I can place a bomb to destroy soft-blocks once my bombCount increases
            if util.goodbombSpot(board,gameState):
            #if this spot is already safe, no need to check for sufficient funds b/c we would've stayed in place anyways
                if gameState['player']['bombPierce'] < 3:
                    return 'buy_pierce'
                if gameState['player']['bombRange'] < 6:
                    return 'buy_range'
                if gameState['player']['bombCount'] < 2:
                    return 'buy_count'

            else:
            #move to a safe spot so that we can place a bomb as soon as our bombCount increases
                escapePath = util.findPath(board,board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsUpcomingTrail",False,allowSoftBlocks=False,allowOpponent=False)
                print("escape path: {0}\nnext block is: {1}".format(escapePath,escapePath[-1]))
                if (not escapePath[-1].containsTrail):
                    if (escapePath[-1].type == SpaceType.softBlock):
                        # todo: we should probably do something here even though the next space in our path is currently a soft block
                        return ''
                    return util.moveTo(gameState,escapePath[-1])

                #To-Do: I've moved to a location that is safe from existing bombs, now make stronger constraint where I can place a bomb to destroy soft-blocks

    else:

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