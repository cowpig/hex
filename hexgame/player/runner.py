execfile("player.py")

if __name__ == "__main__":
	while True:
		game_state = raw_input()
		if game_state.starts_with("game_over"):
			break
		print next_move(game_state)

	# signal rails to tear down docker