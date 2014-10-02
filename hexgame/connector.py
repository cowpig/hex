import api
import time
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--a_ord", dest="a_ord",
                        help="orders file for player A", metavar="FILE")
    parser.add_option("", "--b_ord", dest="b_ord",
                        help="orders file for player B", metavar="FILE")
    
    parser.add_option("", "--a_state", dest="a_state",
                        help="gamestate file for player A", metavar="FILE")
    parser.add_option("", "--b_state", dest="b_state",
                        help="gamestate file for player B", metavar="FILE")

    parser.add_option("-t", "--test", dest="test",
                        help="test the game engine", action="store_true")
    (options, args) = parser.parse_args()

    if options.test:
        import subprocess, os
        orders_a = "orders_a.txt"
        orders_b = "orders_b.txt"
        state_a = "state_a.txt"
        state_b = "state_b.txt"

        player = os.path.join(os.path.dirname(__file__), "player/example_player.py")

        proc_a = subprocess.Popen(["python", player, orders_a, state_a])
        proc_b = subprocess.Popen(["python", player, orders_b, state_b])

        connA = api.PlayerConnection(orders_a, state_a, "A")
        connB = api.PlayerConnection(orders_b, state_b, "B")
    else:
        connA = api.PlayerConnection(options.a_ord, options.a_state, "A")
        connB = api.PlayerConnection(options.b_ord, options.b_state, "B")

    api = api.GameApi(connA, connB)

    # start a new game
    starting_state = api.new_game()
    print api.game.board
    
    # wait 3 seconds before first move
    time.sleep(2)

    while not api.game.game_over:
        try:
            api.next_move()
            print api.game.board
            # 0.3 seconds per move
            time.sleep(.5)
        except KeyboardInterrupt:
            import pdb; pdb.set_trace()

    # update database with winner/loser/gamestate/etc
    print "The game is over and the winner is player {}".format(api.game.winner.id) 

    if options.test:
        proc_a.terminate()
        proc_b.terminate()
