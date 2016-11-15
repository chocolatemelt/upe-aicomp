import bomberman.space as sp

# networking constants
username = "kzhaaang"
devkey = "5823b8c404d7ce4a44c37ab4"
qualifierURL = "http://aicomp.io/api/games/practice" # practice qualifier bot
rankedURL = "http://aicomp.io/api/games/search" # ranked matchmaking vs other AI

# game constants
gameID = '' # id of current game session
playerID = '' # player number
boardSize = -1 # number of units in grid row or column
board = [] # game board (to be re-populated each turn)

#initializes several global constants at gameStart
def setInitialConstants(gameState):
    global gameID, playerID, boardSize
    gameID = gameState['gameID']
    playerID = gameState['playerID']
    boardSize = int(gameState['boardSize'])

# populates a 2d-list of 'Space' objects which contain information about what they contain, as well as whether or not they are in range of an explosion Trail
# todo: currently assumes 0 pierce
def populateBoard(gameState):
    global board
    board = []
    for i in range(boardSize):
        board.append([])
    # first create all spaces
    for i in range(boardSize):
        for r in range(boardSize):
            board[r].append(sp.Space(gameState,r,i))
    # now check space properties that require an initialized board
    for i in range(boardSize):
        for r in range(boardSize):
            board[r][i].initializeLateProperties(gameState)