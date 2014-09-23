execfile("player.py")

if __name__ == "__main__":
	print "I am starting up..."
	while True:
		print "I am in the while loop..."
		game_state = raw_input()
		if game_state.starts_with("game_over"):
			break
		print next_move(game_state)

	print "I am exiting."

	# signal rails to tear down docker