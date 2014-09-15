import game_api
import time
from optparse import OptionParser



if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-a_in", "--a_input", dest="filename",
						help="input file for player A", metavar="FILE")
	parser.add_option("-b_in", "--b_input", dest="filename",
						help="input file for player B", metavar="FILE")
	
	parser.add_option("-a_out", "--a_output", dest="filename",
						help="output file for player A", metavar="FILE")
	parser.add_option("-b_out", "--b_output", dest="filename",
						help="output file for player B", metavar="FILE")


	(options, args) = parser.parse_args()

	connA = game_api.PlayerConnection(options['a_in'], options['a_out'])
	connB = game_api.PlayerConnection(options['b_in'], options['b_out'])

	api = game_api.GameApi(connA, connB)

	# start a new game
	starting_state = api.new_game()

	# wait 3 seconds before first move
	time.sleep(3)

	while not api.game.game_over:
		api.next_move()
		print api.game.board
		# 0.3 seconds per move
		time.sleep(0.3)

	# update database with winner/loser/gamestate/etc

	print "that's all she wrote!"
