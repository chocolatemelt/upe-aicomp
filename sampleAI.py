import requests # if not installed already, run python -m pip install requests OR pip install requests, whatever you normally do

#constants for networking
username = "kzhaaang"
devkey = "5823b8c404d7ce4a44c37ab4"

r = requests.post('http://aicomp.io/api/games/search', data={'devkey': devkey, 'username': username}) # search for new game
json = r.json() # when request comes back, that means you've found a match! (validation if server goes down?)
print(json)
gameID = json['gameID']
playerID = json['playerID']
print(gameID)
print(playerID)
possibleMoves = ['mu', 'ml', 'mr', 'md', 'tu', 'tl', 'tr', 'td', 'b', '', 'op', 'bp', 'buy_count', 'buy_range', 'buy_pierce', 'buy_block']
output = {'state': 'in progress'}
while output['state'] != 'complete':
    moveChoice = 0 #todo: we should actually calculate a move here based on board / game state
    r = requests.post('http://aicomp.io/api/games/submit/' + gameID, data={'playerID': playerID, 'move': possibleMoves[moveChoice], 'devkey': devkey}); # submit sample move
    json = r.json()
    print(json)
    output = json
    