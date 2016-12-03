'''
Created on Nov 29, 2016

@author: Ryan
'''
from enum import Enum
SpaceType = Enum("SpaceType", "empty softBlock hardBlock") # Enum of valid spaces
def getAdjacentSpaces(board,space,direction="all"):
        """return a list of all valid adjacent spaces (direction specified as left, right, up, and down)"""
        #if an x,y coord string is passed in for space, treat it as an empty object with x,y keys
        if type(space) == str:
            strToSpace = type('', (), {})()
            strToSpace.x = int(space.split(",")[0])
            strToSpace.y = int(space.split(",")[1])
            space = strToSpace
            
        adjacentSpaces = []
        if (direction in ("left","all") and space.x > 0):
            adjacentSpaces.append(board[space.x-1][space.y])
        if (direction in ("up","all") and space.y > 0):
            adjacentSpaces.append(board[space.x][space.y-1])
        if (direction in ("right","all") and space.x < len(board) - 1):
            adjacentSpaces.append(board[space.x+1][space.y])
        if (direction in ("down","all") and space.y < len(board) - 1):
            adjacentSpaces.append(board[space.x][space.y+1])
        return None if len(adjacentSpaces) == 0 else adjacentSpaces[0] if direction != "all" else adjacentSpaces
    
    
def getComplementaryPortalCoord(gameState,entrancePortalCoord):
    """return the coordinates of the portal complementary to the entrance portal, if it exists"""
    portalKeys = gameState['portalMap'].keys()
    for coord in portalKeys:
        #print(list(gameState['portalMap'][coord].values())[0])
        if (list(gameState['portalMap'][coord].values())[0]['owner'] == list(gameState['portalMap'][entrancePortalCoord].values())[0]['owner']) and (list(gameState['portalMap'][coord].values())[0]['portalColor'] != list(gameState['portalMap'][entrancePortalCoord].values())[0]['portalColor']):
            return coord
    return None   

def portalExitSpace(board,gameState,entranceSpace):
    """return the space that the portal contained in entranceSpace leads to"""
    if (entranceSpace.containsPortal and gameState['portalMap'][entranceSpace.containedPortalCoord] != {}):
        correspondingPortalCoord = getComplementaryPortalCoord(gameState,entranceSpace.containedPortalCoord)
        if (correspondingPortalCoord == None):
            return None
        correspondingColor = list(gameState['portalMap'][correspondingPortalCoord].values())[0]['portalColor']
        playerString = "player" if (list(gameState['portalMap'][correspondingPortalCoord].values())[0]['owner'] == gameState['playerIndex']) else "opponent"
        direction = gameState[playerString][correspondingColor + "Portal"]['direction']
        adjacentSpace = getAdjacentSpaces(board,correspondingPortalCoord,("left","up","right","down")[int(direction)])
        return adjacentSpace

def canTraversePortal(board,gameState,currentSpace,newSpace):
    """return whether or not newSpace contains a portal facing currentSpace, which leads to a walkable space"""
    if (newSpace.containsPortal and gameState['portalMap'][newSpace.containedPortalCoord] != {}):
        #print(gameState['portalMap'])
        #todo: didn't realize that key of portalMap is portal direction, so we can eliminate direction finding code and simply use this key
        #print(gameState['portalMap'][newSpace.containedPortalCoord])
        correspondingColor = list(gameState['portalMap'][newSpace.containedPortalCoord].values())[0]['portalColor']
        playerString = "player" if (list(gameState['portalMap'][newSpace.containedPortalCoord].values())[0]['owner'] == gameState['playerIndex']) else "opponent"
        direction = gameState[playerString][correspondingColor+"Portal"]['direction']
        adjacentSpace = getAdjacentSpaces(board,newSpace.containedPortalCoord,("left","up","right","down")[int(direction)])
        if (adjacentSpace == currentSpace):
            exitSpace = portalExitSpace(board,gameState,newSpace)
            return (exitSpace != None and exitSpace.type == SpaceType.empty),exitSpace
    return (False,None)