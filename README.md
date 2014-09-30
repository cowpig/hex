# hex #
=======

This is a game to be played by computer players in an upcoming competition in Montreal: the <a href="http://machineintelligencecup.com">Machine Intelligence Cup</a>

Un jeux pour la compétition à venir à Montréal: le <a href="http://machineintelligencecup.com"> Coupe Intelligence Artificielle </a>

It will look something like this:

![alt tag](https://raw.github.com/cowpig/hex/master/demo.png)

## Game Engine ##

The engine is working. A fully working demo can be played with:

```python hexgame/connector.py --test```

A mock connection between two players will be set, and both players will run the code from `hexgame/players/example_player.py`, in which each player will move pieces randomly one space at a time, unless the enemy's home is in vision, in which case any piece that can will attack it.

## TODO: Frontend ##

The front end is still rather incomplete. Running:

```python hexgame/websocket_test.py```

will open a server that will interact with `user_interface/hex_grid_demo.html`, which is still very much incomplete. `user_interface/js/HexagonTools.js` and `user_interface/js/Grid.js` contain a bleeding-edge library for dealing with drawing hexagonal maps to a canvas.

## TODO: Web Backend ##

Eventually, this will interact with [codebin](https://github.com/surenm/codebin), so that players of the game can upload code, get paired with another player, and watch the game being played out. [Codebin](https://github.com/surenm/codebin) creates docker containers limited to a single cpu core and limited memory for each player, to create a safe (for the server) and balanced (for the players) environment to run the players' AIs.