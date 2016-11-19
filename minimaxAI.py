"""AI designed to make intelligent move selections based on future gameStates using minimax tree"""
from space import Space, SpaceType #custom space class containing information about a given board position
import utilities as util#several misc functions that are unrelated to functionality or not specific to AI

def chooseMove(board,gameState): # todo: put move selection logic here
    """called each turn. generates tree of potential future gameStates, then selects the Node leading to the least loss"""
    #full list of moves (copied from sampleAI)
    possibleMoves = ['mu', 'ml', 'mr', 'md', 'tu', 'tl', 'tr', 'td', 'b', '', 'op', 'bp', 'buy_count', 'buy_range', 'buy_pierce', 'buy_block']
    return ""