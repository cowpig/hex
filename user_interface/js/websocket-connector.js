"use strict";

var wsUri = "ws://localhost:8000/ws";
var websocket = new WebSocket(wsUri);
var grid;
var statusBar;
var canvas;


function init() { 
	console.log("also herr");
	statusBar = document.getElementById("status");
	if (!'WebSocket' in window){
		console.log ("no websocket");
		writeToScreen('<span style="color: red;">ERROR: Update your browser to one that supports websockets. A list can be found <a href="http://caniuse.com/websockets">here</a></span>');
	} else {
		canvas = $("#hexCanvas");
		prepareWebsocket();
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

$("document").ready(init);
