import game_api
import time
from optparse import OptionParser

import example_player

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--a_input", dest="a_in",
                        help="input file for player A", metavar="FILE")
    parser.add_option("", "--b_input", dest="a_out",
                        help="input file for player B", metavar="FILE")
    
    parser.add_option("", "--a_output", dest="b_in",
                        help="output file for player A", metavar="FILE")
    parser.add_option("", "--b_output", dest="b_out",
                        help="output file for player B", metavar="FILE")

    parser.add_option("-t", "--test", dest="test",
                        help="test the game engine", action="store_true")
    (options, args) = parser.parse_args()

    if options["test"]:
        connA = game_api.MockConnection()
        connB = game_api.MockConnection()
    else:
        connA = game_api.PlayerConnection(options['a_input'], options['a_output'])
        connB = game_api.PlayerConnection(options['b_input'], options['b_output'])

    api = game_api.GameApi(connA, connB)

    # start a new game
    starting_state = api.new_game()
    print api.game.board
    
    # wait 3 seconds before first move
    time.sleep(3)

    while not api.game.game_over:
        api.next_move()
        print api.game.board
        # 0.3 seconds per move
        time.sleep(0.3)

    # update database with winner/loser/gamestate/etc
    print "The game is over and the winner is player {}".format(api.game.winner.id) 
