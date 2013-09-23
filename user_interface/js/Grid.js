var Game = Game || {};

// takes the output of a Hex board to initialize
Game.Board = function(width, height, starting_input) {
	this.map = {};
	for (var i=0; i<starting_input.length; i++){
		var p = Hex.Point(input.coord[0], input.coord[1]);
		this.map[p] = {
			'contents':input.contents
		};
	}
};

Game.Item = function(id) {
	this.Id = id;
}

Game.Item.prototype.get_owner = function() {
	if (this.Id.charAt(0) === "A")
		return "A";
	if (this.Id.charAt(0) === "B")
		return "B";
	return null;
}

// TODO: decide whether to encode everything in Id or create instance variables
Game.Item.prototype.get_range = function() {
	if (this.Id.charAt(0))
}