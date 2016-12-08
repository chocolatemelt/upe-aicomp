"""test AI designed to examine apocalypse functionality"""
from space import Space, SpaceType #custom space class containing information about a given board position
import utilities as util#several misc functions that are unrelated to functionality or not specific to AI

def chooseMove(board,gameState):
    """called once per turn. Calls pathfinding to get as close to the center of the stage as possible, in order to test ring of fire adequately"""
    def escapeTrail(): #COPIED FROM RATCHET FOR TESTING!
        """returns a command to move to the next space if we are in danger of an explosion Trail, or None if we are safe"""
        # if we are not currently on a space that is slated to contain a trail, we don't need to do anything
        if (not board[int(gameState['player']['x'])][int(gameState['player']['y'])].containsUpcomingTrail):
            return None
        escapePath = util.findPath(gameState,board,board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsUpcomingTrail",False,allowSoftBlocks=False,allowOpponent=False)
        print("escape path: {0}\nnext block is: {1}".format(escapePath,escapePath[-1]))
        if (escapePath == None): # todo: we should probably do something here even though we couldn't find a path to escape
            return ''
        if (not escapePath[-1].containsTrail):
            if (escapePath[-1].type == SpaceType.softBlock):
                # todo: we should probably do something here even though the next space in our path is currently a soft block
                return ''
            return util.moveTo(gameState,board,escapePath[-1])
        else:
            # todo: we should probably do something here even though the next space in our path is currently lethal
            return ''
        
    def approachCenter(): #MOSTLY COPIED FROM RATCHET FOR TESTING!
        "returns a command to move towards the center space, blowing up any blocks in the way"
        approachPath = util.findPath(gameState,board,board[int(gameState['player']['x'])][int(gameState['player']['y'])],"isCenterSpace")
        print("approach path: {0}\nnext block is: {1}".format(approachPath,approachPath[-1]))
        if (approachPath == None or len(approachPath) == 0): # todo: we should probably do something here even though we couldn't find a path to approach (this state may be unreachable though depending on implementation)
            return ''
        if (not (approachPath[-1].containsTrail or approachPath[-1].containsUpcomingTrail)): #don't approach into a trail OR an upcoming trail todo: check number of ticks on upcoming trail instead
            if (approachPath[-1].type == SpaceType.softBlock or approachPath[-1].containsOpponent): # place a bomb if we are right next to a soft block or the opponent
                return "b" # todo: this assumes that we currently have a bomb available. Account for case when we do not have any bombs available to use
                
            return util.moveTo(gameState,board,approachPath[-1])
        else:
        # todo: we should probably do something here even though the next space in our path is currently lethal
            return ''
        
    move = escapeTrail()
    if (move == None):
        move = approachCenter()
    return move