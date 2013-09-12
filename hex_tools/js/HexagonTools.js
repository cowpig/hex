// This is all adapted from a script found at:
// http://www.mattpalmerlee.com/2012/04/05/fun-with-hexagon-math-for-games/

var HT = HT || {};
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

/**
 * A Hexagon is a 6 sided polygon, our hexes don't have to be symmetrical, i.e. ratio of width to height could be 4 to 3
 * @constructor
 */
Hex.Hexagon = function(id, x, y, width, height) {
	var y = height/2.0;
	
	//solve quadratic
	var a = -3.0;
	var b = (-2.0 * width);
	var c = (Math.pow(width, 2)) + (Math.pow(height, 2));
	
	var z = (-b - Math.sqrt(Math.pow(b,2)-(4.0*a*c)))/(2.0*a);

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

function drawHexGrid()
{
	var grid = new Grid(800, 600);
	var canvas = document.getElementById("hexCanvas");
	var ctx = canvas.getContext('2d');
	ctx.clearRect(0, 0, 800, 600);
	for(var h in grid.Hexes)
	{
		grid.Hexes[h].draw(ctx);
	}
}