"use strict";

var Game = Game || {};

// takes the output of a Hex board to initialize
Game.Board = function(board_info) {
	console.log("creating Board with data:\n" + board_info);

	this.nodes = board_info['nodes'];
	var nxm = board_info['size'].split(",");

	this.num_x = parseFloat(nxm[0]);
	this.num_y = parseFloat(nxm[1]);

	this.homes = board_info['homes'];

	this.game_state = null;

	this.offsetX = 0;
	this.offsetY = 0;
};

Game.Board.prototype.recenter = function(centerOnX, centerOnY) {
	this.offsetX += centerOnX;
	this.offsetY += centerOnY;
}

Game.Board.prototype.draw = function(game_state, canvas) {

	// console.log(canvas);

	var centerX = canvas[0].width / 2;
	var centerY = canvas[0].height / 2;

	var w_px = canvas[0].width / (0.5 + this.num_x);
	var h_px = w_px;
	// var h_px = (canvas[0].height * this.num_x * w_px) / (canvas[0].width * this.num_y);
	// var h_px_old = canvas[0].height / this.num_y;

	// calculate where each hexagon goes

	// console.log("w_px : " + w_px);
	// console.log("h_px : " + h_px);
	// console.log("num_x : " + this.num_x);
	// console.log("num_y : " + this.num_y);


	// w_px = 20;
	// h_px = 20;

	// console.log("drawing hex grid with input:\n" + game_state);

	//solve quadratic to get side length (z)
	var a = -3.0;
	var b = (-2.0 * w_px);
	var c = (Math.pow(w_px, 2)) + (Math.pow(h_px, 2));
	this.z = (-b - Math.sqrt(Math.pow(b,2)-(4.0*a*c)))/(2.0*a);

	this.total_width = (this.num_x + 0.5) * w_px;
	this.total_height = (this.num_y + 0.5) * (h_px - (h_px-this.z)/2);

	var ctx = canvas[0].getContext('2d');
	

	ctx.fillStyle = "black";
	ctx.clearRect(0, 0, this.total_width, this.total_height);

	console.log("center:", centerX, ",", centerY);

	console.log("Translate back: (", centerX - this.offsetX, centerY - this.offsetY, ")");
	ctx.translate(centerX - this.offsetX, centerY - this.offsetY);

	for (var i in this.nodes){
		var node = this.nodes[i];
		var id = null;
		// console.log(JSON.stringify(node));
		if (node.toString() in this.homes){
			id = this.homes[node.toString()];
			// console.log("home at " + node.toString());
		}
		new Hex.Hexagon(id, null, node[0], node[1], w_px, h_px, this.z).draw(ctx);
	}

	if (this.game_state){
		for (var player in game_state) {
			if (game_state.hasOwnProperty(player)) {
				for (var piece in game_state[player]) {
					var id = player + "_" + piece['id'] + "_" + piece['r'];
					new Hex.Hexagon(id, player, piece['loc'][0], piece['loc'][1], w_px, h_px, this.z);
				}
			}
		}
	}
	console.log("Translate: (", this.offsetX - centerX, this.offsetY - centerY, ")");
	ctx.translate(this.offsetX - centerX, this.offsetY - centerY);

		// TODO: visible range
}



// TODO
// Game.Item.prototype.get_range = function() {
// 	if (this.Id.charAt(0))
// }