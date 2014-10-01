import api
import time
from optparse import OptionParser

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

    if options.test:
        import subprocess, os
        in_a = "in_a.txt"
        in_b = "in_b.txt"
        out_a = "out_a.txt"
        out_b = "out_b.txt"

        player = os.path.join(os.path.dirname(__file__), "player/example_player.py")

        proc_a = subprocess.Popen(["python", player, out_a, in_a])
        proc_b = subprocess.Popen(["python", player, out_b, in_b])

        connA = api.PlayerConnection(in_a, out_a, "A")
        connB = api.PlayerConnection(in_b, out_b, "B")
    else:
        connA = api.PlayerConnection(options['a_input'], options['a_output'], "A")
        connB = api.PlayerConnection(options['b_input'], options['b_output'], "B")

    api = api.GameApi(connA, connB)

    # start a new game
    starting_state = api.new_game()
    print api.game.board
    
    # wait 3 seconds before first move
    time.sleep(1.5)

    while not api.game.game_over:
        try:
            api.next_move()
            print api.game.board
            # 0.3 seconds per move
            time.sleep(0.2)
        except KeyboardInterrupt:
            import pdb; pdb.set_trace()

    # update database with winner/loser/gamestate/etc
    print "The game is over and the winner is player {}".format(api.game.winner.id) 

    if options.test:
        proc_a.terminate()
        proc_b.terminate()
