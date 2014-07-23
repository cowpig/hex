var Game = Game || {};

// takes the output of a Hex board to initialize
Game.Board = function(board, w_px, h_px) {
	console.log("creating Board with data:\n" + board);

	if (w_px === null)
		w_px = 40;
	if (h_px === null)
		h_px = 40;

	this.nodes = board['nodes'];
	var nxm = board['size'].split(",");

	this.num_x = nxm[0];
	this.num_y = nxm[1];

	this.w_px = w_px;
	this.h_px = h_px;

	var a = -3.0;
	var b = (-2.0 * this.w_px);
	var c = (Math.pow(this.w_px, 2)) + (Math.pow(this.h_px, 2));
	this.z = (-b - Math.sqrt(Math.pow(b,2)-(4.0*a*c)))/(2.0*a);

	this.total_width = (this.num_x + 0.5) * this.w_px;
	this.total_height = (this.num_y + 0.5) * (this.h_px - (this.h_px-this.z)/2);

	this.homes = board['homes'];
};

Game.Board.prototype.draw = function(game_state, canvas) {
	// function(input, num_x, num_y, width, height)
	console.log("drawing hex grid with input:\n" + game_state);

	//solve quadratic to get side length

	var ctx = canvas.getContext('2d');
	ctx.fillStyle = "black";
	ctx.clearRect(0, 0, this.total_width, this.total_height);

	for (var i in this.nodes){
		var node = this.nodes[i];
		var id = null;
		console.log(JSON.stringify(node));
		if (node.toString() in this.homes){
			id = this.homes[node.toString()];
			console.log("home at " + node.toString());
		}
		new Hex.Hexagon(id, null, node[0], node[1], this.w_px, this.h_px, this.z).draw(ctx);
	}

	if (game_state){
		for (var player in game_state) {
			if (game_state.hasOwnProperty(player)) {
				for (var piece in game_state[player]) {
					var id = player + "_" + piece['id'] + "_" + piece['r'];
					new Hex.Hexagon(id, player, piece['loc'][0], piece['loc'][1], this.w_px, this.h_px, this.z);
				}
			}
		}
	}

		// TODO: visible range
}



// TODO
// Game.Item.prototype.get_range = function() {
// 	if (this.Id.charAt(0))
// }