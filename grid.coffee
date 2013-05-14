# A Grid is the model of the playfield containing hexes

HT.Grid = (width, height) ->
	@Hexes = []
	
	#setup a dictionary for use later for assigning the X or Y CoOrd (depending on Orientation)
	HexagonsByXOrYCoOrd = {} #Dictionary<int, List<Hexagon>>
	row = 0
	y = 0.0
	while y + HT.Hexagon.Static.HEIGHT <= height
		col = 0
		offset = 0.0
		if row % 2 is 1
			if HT.Hexagon.Static.ORIENTATION is HT.Hexagon.Orientation.Normal
				offset = (HT.Hexagon.Static.WIDTH - HT.Hexagon.Static.SIDE) / 2 + HT.Hexagon.Static.SIDE
			else
				offset = HT.Hexagon.Static.WIDTH / 2
			col = 1
		x = offset
		while x + HT.Hexagon.Static.WIDTH <= width
			hexId = @GetHexId(row, col)
			h = new HT.Hexagon(hexId, x, y)
			pathCoOrd = col
			unless HT.Hexagon.Static.ORIENTATION is HT.Hexagon.Orientation.Normal
				#the column is the x coordinate of the hex, for the y coordinate we need to get more fancy
				h.PathCoOrdY = row
				pathCoOrd = row
			@Hexes.push h
			HexagonsByXOrYCoOrd[pathCoOrd] = []  unless HexagonsByXOrYCoOrd[pathCoOrd]
			HexagonsByXOrYCoOrd[pathCoOrd].push h
			col += 2
			if HT.Hexagon.Static.ORIENTATION is HT.Hexagon.Orientation.Normal
				x += HT.Hexagon.Static.WIDTH + HT.Hexagon.Static.SIDE
			else
				x += HT.Hexagon.Static.WIDTH
		row++
		if HT.Hexagon.Static.ORIENTATION is HT.Hexagon.Orientation.Normal
			y += HT.Hexagon.Static.HEIGHT / 2
		else
			y += (HT.Hexagon.Static.HEIGHT - HT.Hexagon.Static.SIDE) / 2 + HT.Hexagon.Static.SIDE
	
	#finally go through our list of hexagons by their x co-ordinate to assign the y co-ordinate
	for coOrd1 of HexagonsByXOrYCoOrd
		hexagonsByXOrY = HexagonsByXOrYCoOrd[coOrd1]
		coOrd2 = Math.floor(coOrd1 / 2) + (coOrd1 % 2)
		for i of hexagonsByXOrY
			h = hexagonsByXOrY[i] #Hexagon
			if HT.Hexagon.Static.ORIENTATION is HT.Hexagon.Orientation.Normal
				h.PathCoOrdY = coOrd2++
			else
				h.PathCoOrdX = coOrd2++

HT.Grid.Static = Letters: "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HT.Grid::GetHexId = (row, col) ->
	letterIndex = row
	letters = ""
	while letterIndex > 25
		letters = HT.Grid.Static.Letters[letterIndex % 26] + letters
		letterIndex -= 26
	HT.Grid.Static.Letters[letterIndex] + letters + (col + 1)


###
Returns a hex at a given point
@this {HT.Grid}
@return {HT.Hexagon}
###
HT.Grid::GetHexAt = (p) -> #Point
	
	#find the hex that contains this point
	for h of @Hexes
		return @Hexes[h]  if @Hexes[h].Contains(p)
	null


###
Returns a distance between two hexes
@this {HT.Grid}
@return {number}
###
HT.Grid::GetHexDistance = (h1, h2) -> 
	#a good explanation of this calc can be found here:
	#http://playtechs.blogspot.com/2007/04/hex-grids.html
	deltaX = h1.PathCoOrdX - h2.PathCoOrdX
	deltaY = h1.PathCoOrdY - h2.PathCoOrdY
	(Math.abs(deltaX) + Math.abs(deltaY) + Math.abs(deltaX - deltaY)) / 2


###
Returns a distance between two hexes
@this {HT.Grid}
@return {HT.Hexagon}
###
HT.Grid::GetHexById = (id) ->
	for i of @Hexes
		return @Hexes[i]  if @Hexes[i].Id is id
	null