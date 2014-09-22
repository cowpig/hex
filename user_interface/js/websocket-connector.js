"use strict";

var wsUri = "ws://localhost:8000/ws";
var websocket = new WebSocket(wsUri);
var grid;
var statusBar;
var canvas;


function init() { 
	statusBar = document.getElementById("status");
	if (!'WebSocket' in window){
		console.log ("no websocket");
		writeToScreen('<span style="color: red;">ERROR: Update your browser to one that supports websockets. A list can be found <a href="http://caniuse.com/websockets">here</a></span>');
	} else {
		canvas = $("#hexCanvas");
		prepareWebsocket();
		canvas.click(moveMap);
	}
}

function onOpen(evt) { 
	writeToScreen("CONNECTED");
	websocket.send("newgame");
}

function onClose(evt) { 
	writeToScreen("DISCONNECTED");
}

function onMessage(evt) {
	console.log("data received:\n" + JSON.stringify(evt));
	var data = evt.data.split("&=");

	if (data[0] == "board"){
		grid = new Game.Board(JSON.parse(data[1]));
		resizeCanvas();
		grid.draw(null, canvas);
	}

}

function onError(evt) { 
	writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
}

function prepareWebsocket() {
	websocket.onopen = function(evt) { onOpen(evt) };
	websocket.onclose = function(evt) { onClose(evt) };
	websocket.onmessage = function(evt) { onMessage(evt) };
	websocket.onerror = function(evt) { onError(evt) };
	$("#send").on("click", function () {
		websocket.send(document.getElementById("inputTxt").value);
		console.log("click registered.");
	});
}

function writeToScreen(message) { 
	statusBar.innerHTML = message;
}

function resizeCanvas(e) {
	var map = $("#map");
	canvas[0].height = map.height();
	canvas[0].width = map.width();
	grid.draw(null, canvas);
	// console.log(e);
}

function moveMap(e) {
	// console.log(e);
	var x = e.clientX;
	var y = e.clientY;
	console.log("click: (", x, ", ", y, ")");
	grid.recenter(x - canvas[0].width / 2, y - canvas[0].height / 2);
	grid.draw(null, canvas);
}


$("document").ready(init);
// $(window).resize(resizeCanvas);