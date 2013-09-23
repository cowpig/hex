var Board = Board || {};

// takes the output of a Hex board to initialize
Board.Grid = function(width, height, starting_input) {
	this.map = {};
	for (var i=0; i<starting_input.length; i++){
		var p = Hex.Point(input.coord[0], input.coord[1]);
		this.map[p] = input.contents;
	}
};