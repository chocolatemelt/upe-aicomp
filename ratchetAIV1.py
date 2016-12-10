"""basic AI designed to overcome basic, common circumstances in order to beat random the qualifier bot"""
from space import Space, SpaceType #custom space class containing information about a given board position
import utilities as util#several misc functions that are unrelated to functionality or not specific to AI

def chooseMove(board,gameState):
    """called once per turn. Calls either escapeTrail or approachOpponent to determine move choice"""
    def escapeTrail():
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

    def approachOpponent():
        """returns a command to move to the next space in order to approach the opponent, or a bomb command if in range to hit opponent"""
        approachPath = util.findPath(gameState,board,board[int(gameState['player']['x'])][int(gameState['player']['y'])],"containsOpponent")
        print("approach path: {0}\nnext block is: {1}".format(approachPath,approachPath[-1]))
        if (approachPath == None): # todo: we should probably do something here even though we couldn't find a path to approach (this state may be unreachable though depending on implementation)
            return ''
        if (not (approachPath[-1].containsTrail or approachPath[-1].containsUpcomingTrail)): #don't approach into a trail OR an upcoming trail todo: check number of ticks on upcoming trail instead
            if (approachPath[-1].type == SpaceType.softBlock or approachPath[-1].containsOpponent): # place a bomb if we are right next to a soft block or the opponent
                return "b" # todo: this assumes that we currently have a bomb available. Account for case when we do not have any bombs available to use
                
            return util.moveTo(gameState,board,approachPath[-1])
        else:
        # todo: we should probably do something here even though the next space in our path is currently lethal
            return ''

    def tryPurchaseUpgrade():
        # attempt to select an upgrade to purchase
        # we only buy pierce up til 3 (max pierce for range 3)
        if(gameState['player']['bombPierce'] < 3):
            return "buy_pierce"
        return ''

    move = escapeTrail()
    if (move == None):
        move = approachOpponent()
    if (move == None or move == ""):
        move = tryPurchaseUpgrade()
    return move
