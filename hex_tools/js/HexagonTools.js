// This is all adapted from a script found at:
// http://www.mattpalmerlee.com/2012/04/05/fun-with-hexagon-math-for-games/

var Hex = Hex || {};
/**
 * A Point is simply x and y coordinates
 * @constructor
 */
Hex.Point = function(x, y) {
	this.X = x;
	this.Y = y;
};

/**
 * A Rectangle is x and y origin and width and height
 * @constructor
 */
Hex.Rectangle = function(x, y, width, height) {
	this.X = x;
	this.Y = y;
	this.Width = width;
	this.Height = height;
};

/**
 * A Line is x and y start and x and y end
 * @constructor
 */
Hex.Line = function(x1, y1, x2, y2) {
	this.X1 = x1;
	this.Y1 = y1;
	this.X2 = x2;
	this.Y2 = y2;
};

// determines the side length of a hexagon, given its height and width
Hex.get_z = function(width, height) {
}

/**
 * A Hexagon is a 6 sided polygon, our hexes don't have to be symmetrical, i.e. ratio of width to height could be 4 to 3
 * @constructor
 */
Hex.Hexagon = function(id, xpos, ypos, width, height, z) {

	console.log(id + "," + xpos + "," + ypos + "," + width + "," + height + "," + z)

	var x = xpos * width;
	if (ypos % 2 === 1)
		x += width / 2;
	var y = ypos * (height - (height-z)/2);

	console.log("creating hex at (" + x + ", " + y + ")");

	this.Points = [];//Polygon Base
	var x1 = null;
	var y1 = null;

	x1 = (width / 2);
	y1 = (height - z)/2;
	this.Points.push(new Hex.Point(x1 + x, y));
	this.Points.push(new Hex.Point(width + x, y1 + y));
	this.Points.push(new Hex.Point(width + x, y1 + z + y));
	this.Points.push(new Hex.Point(x1 + x, height + y));
	this.Points.push(new Hex.Point(x, y1 + z + y));
	this.Points.push(new Hex.Point(x, y1 + y));
	
	this.Id = id;
	
	this.x = x;
	this.y = y;
	this.x1 = x1;
	this.y1 = y1;
	
	this.TopLeftPoint = new Hex.Point(this.x, this.y);
	this.BottomRightPoint = new Hex.Point(this.x + width, this.y + height);
	this.MidPoint = new Hex.Point(this.x + (width / 2), this.y + (height / 2));
	
	this.P1 = new Hex.Point(x + x1, y + y1);
	
	this.selected = false;
};
	
/**
 * draws this Hexagon to the canvas
 * @this {Hex.Hexagon}
 */
Hex.Hexagon.prototype.draw = function(ctx) {

	if(!this.selected)
		ctx.strokeStyle = "grey";
	else
		ctx.strokeStyle = "black";
	ctx.lineWidth = 1;
	ctx.beginPath();
	ctx.moveTo(this.Points[0].X, this.Points[0].Y);
	for(var i = 1; i < this.Points.length; i++)
	{
		var p = this.Points[i];
		ctx.lineTo(p.X, p.Y);
	}
	ctx.closePath();
	ctx.stroke();
	
	if(this.Id)
	{
		//draw text for debugging
		ctx.fillStyle = "black"
		ctx.font = "bolder 8pt Trebuchet MS,Tahoma,Verdana,Arial,sans-serif";
		ctx.textAlign = "center";
		ctx.textBaseline = 'middle';
		//var textWidth = ctx.measureText(this.Planet.BoundingHex.Id);
		ctx.fillText(this.Id, this.MidPoint.X, this.MidPoint.Y);
	}
	
	// if(this.PathCoOrdX !== null && this.PathCoOrdY !== null && typeof(this.PathCoOrdX) != "undefined" && typeof(this.PathCoOrdY) != "undefined")
	// {
	// 	//draw co-ordinates for debugging
	// 	ctx.fillStyle = "black"
	// 	ctx.font = "bolder 8pt Trebuchet MS,Tahoma,Verdana,Arial,sans-serif";
	// 	ctx.textAlign = "center";
	// 	ctx.textBaseline = 'middle';
	// 	//var textWidth = ctx.measureText(this.Planet.BoundingHex.Id);
	// 	ctx.fillText("("+this.PathCoOrdX+","+this.PathCoOrdY+")", this.MidPoint.X, this.MidPoint.Y + 10);
	// }
	
	// if(Hex.Hexagon.Static.DRAWSTATS)
	// {
	// 	ctx.strokeStyle = "black";
	// 	ctx.lineWidth = 2;
	// 	//draw our x1, y1, and z
	// 	ctx.beginPath();
	// 	ctx.moveTo(this.P1.X, this.y);
	// 	ctx.lineTo(this.P1.X, this.P1.Y);
	// 	ctx.lineTo(this.x, this.P1.Y);
	// 	ctx.closePath();
	// 	ctx.stroke();
		
	// 	ctx.fillStyle = "black"
	// 	ctx.font = "bolder 8pt Trebuchet MS,Tahoma,Verdana,Arial,sans-serif";
	// 	ctx.textAlign = "left";
	// 	ctx.textBaseline = 'middle';
	// 	//var textWidth = ctx.measureText(this.Planet.BoundingHex.Id);
	// 	ctx.fillText("z", this.x + this.x1/2 - 8, this.y + this.y1/2);
	// 	ctx.fillText("x", this.x + this.x1/2, this.P1.Y + 10);
	// 	ctx.fillText("y", this.P1.X + 2, this.y + this.y1/2);
	// 	ctx.fillText("z = " + Hex.Hexagon.Static.SIDE, this.P1.X, this.P1.Y + this.y1 + 10);
	// 	ctx.fillText("(" + this.x1.toFixed(2) + "," + this.y1.toFixed(2) + ")", this.P1.X, this.P1.Y + 10);
	// }
};

/**
 * Returns true if the x,y coordinates are inside this hexagon
 * @this {Hex.Hexagon}
 * @return {boolean}
 */
Hex.Hexagon.prototype.isInBounds = function(x, y) {
	return this.Contains(new Hex.Point(x, y));
};
	

/**
 * Returns true if the point is inside this hexagon, it is a quick contains
 * @this {Hex.Hexagon}
 * @param {Hex.Point} p the test point
 * @return {boolean}
 */
Hex.Hexagon.prototype.isInHexBounds = function(/*Point*/ p) {
	if(this.TopLeftPoint.X < p.X && this.TopLeftPoint.Y < p.Y &&
	   p.X < this.BottomRightPoint.X && p.Y < this.BottomRightPoint.Y)
		return true;
	return false;
};

//grabbed from:
//http://www.developingfor.net/c-20/testing-to-see-if-a-point-is-within-a-polygon.html
//and
//http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html#The%20C%20Code
/**
 * Returns true if the point is inside this hexagon, it first uses the quick isInHexBounds contains, then check the boundaries
 * @this {Hex.Hexagon}
 * @param {Hex.Point} p the test point
 * @return {boolean}
 */
Hex.Hexagon.prototype.Contains = function(/*Point*/ p) {
	var isIn = false;
	if (this.isInHexBounds(p))
	{
		//turn our absolute point into a relative point for comparing with the polygon's points
		//var pRel = new Hex.Point(p.X - this.x, p.Y - this.y);
		var i, j = 0;
		for (i = 0, j = this.Points.length - 1; i < this.Points.length; j = i++)
		{
			var iP = this.Points[i];
			var jP = this.Points[j];
			if (
				(
				 ((iP.Y <= p.Y) && (p.Y < jP.Y)) ||
				 ((jP.Y <= p.Y) && (p.Y < iP.Y))
				//((iP.Y > p.Y) != (jP.Y > p.Y))
				) &&
				(p.X < (jP.X - iP.X) * (p.Y - iP.Y) / (jP.Y - iP.Y) + iP.X)
			   )
			{
				isIn = !isIn;
			}
		}
	}
	return isIn;
};
	var input = [{"neighbors": 4, "type": "node", "contents": "", "coord": [3, 8]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [0, 6]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [1, 2]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [8, 1]},
     {"neighbors": 2, "type": "node", "contents": "", "coord": [6, 4]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [1, 6]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [8, 9]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [4, 3]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [3, 7]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [6, 9]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [2, 1]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [2, 7]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [8, 5]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [1, 5]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [1, 7]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [2, 0]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [9, 0]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [2, 8]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [6, 2]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [3, 1]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [8, 7]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [2, 5]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [6, 5]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [2, 9]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [2, 6]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [9, 6]},
     {"neighbors": 1, "type": "node", "contents": "", "coord": [7, 2]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [7, 5]},
     {"neighbors": 6, "type": "node", "contents": "#", "coord": [2, 3]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [8, 8]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [2, 2]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [4, 4]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [1, 1]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [5, 2]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [7, 7]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [1, 0]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [3, 5]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [7, 8]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [4, 1]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [0, 9]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [8, 6]},
     {"neighbors": 6, "type": "node", "contents": "#", "coord": [0, 8]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [6, 8]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [4, 2]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [3, 3]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [0, 0]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [2, 4]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [3, 6]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [0, 2]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [6, 7]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [3, 2]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [0, 1]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [1, 3]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [8, 0]},
     {"neighbors": 3, "type": "node", "contents": "", "coord": [0, 4]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [3, 4]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [0, 5]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [1, 4]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [1, 8]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [7, 9]},
     {"neighbors": 4, "type": "node", "contents": "", "coord": [5, 3]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [9, 9]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [7, 6]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [0, 7]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [9, 5]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [9, 8]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [1, 9]},
     {"neighbors": 5, "type": "node", "contents": "", "coord": [9, 1]},
     {"neighbors": 6, "type": "node", "contents": "", "coord": [9, 7]}];

function drawHexGrid()
{
	var num_x = 10;
	var num_y = 10;
	var width = 60;
	var height = 60;


	//solve quadratic
	var a = -3.0;
	var b = (-2.0 * width);
	var c = (Math.pow(width, 2)) + (Math.pow(height, 2));
	var z = (-b - Math.sqrt(Math.pow(b,2)-(4.0*a*c)))/(2.0*a);


	var total_width = (num_x + 0.5) * width;
	var total_height = num_y * (height - (height-z)/2);

	var canvas = document.getElementById("hexCanvas");
	var ctx = canvas.getContext('2d');
	ctx.fillstyle = "black";
	ctx.clearRect(0, 0, total_width, total_height);

	for (var i=0; i<input.length; i++)
	{
		var node = input[i];
		console.log(JSON.stringify(node));
		xpos = node.coord[0];
		ypos = node.coord[1];
		if (node.contents != "")
			var id = node.contents;
		else
			var id = "";
			// var id = "(" + xpos + ", " + ypos + ")";
		console.log("(" + xpos + ", " + ypos + ")");
		new Hex.Hexagon(id, xpos, ypos, width, height, z).draw(ctx);
	}
}