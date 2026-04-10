🐺🐐🥬 River Crossing Ultra Promax

A visually enhanced Python Tkinter game based on the classic Wolf, Goat, and Cabbage river crossing puzzle. This project combines logical problem-solving with an interactive GUI, smooth boat animation, realistic vector-style characters, move history tracking, hint support, and an automatic solver.

📌 Project Description

In this puzzle, a farmer must safely transport a wolf, a goat, and a cabbage from the left bank of a river to the right bank using a boat. The challenge lies in the rules:

The boat can carry only the farmer and one item at a time
The wolf cannot be left alone with the goat
The goat cannot be left alone with the cabbage

The objective is to move all characters safely across the river without violating these constraints.

This project brings that classic AI puzzle to life with a polished desktop interface and interactive gameplay. The code includes a dedicated game engine for puzzle logic and a Tkinter-based GUI for rendering the scene, managing controls, animating the boat, and displaying game status .

✨ Features

Interactive desktop GUI built with Tkinter
Classic river crossing logic with rule validation
Smooth animated boat movement between river banks
Custom-drawn characters for:
Farmer
Wolf
Goat
Cabbage
Hint system for guiding the next correct move
Auto Solve option using a predefined valid solution path
Move history panel
Timer to track completion time
Move counter
Day / Night visual mode toggle
Win and game-over screens
Restart support for replayability

🧠 Problem Type

This project represents a classic Artificial Intelligence state-space search problem. It can also be viewed as:

A constraint satisfaction problem
A goal-based problem
A logic and decision-making puzzle

The engine maintains the state of the left and right river banks, validates moves, and checks whether the player has won or entered an invalid state .

⚙️ How It Works

The game logic is handled by the RiverCrossingEngine class, which:

Stores the current positions of the farmer, wolf, goat, and cabbage
Tracks move history
Generates possible moves
Validates whether a move creates an unsafe state
Detects the win condition
Stores the correct puzzle solution for hints and auto solve

The GUI is handled by the RiverCrossingUltraPromax class, which:

Creates the application window
Draws the river, banks, boat, sky, and characters
Updates positions after each move
Animates boat travel
Displays status messages, timer, and move history
Provides control buttons such as Start, Restart, Hint, Auto Solve, Day/Night, and Rules

🎮 Controls

The game includes the following actions:

Start Game — begins a new session
Restart — resets the puzzle
Farmer Alone — sends the farmer alone across the river
Take Wolf
Take Goat
Take Cabbage
Hint — suggests the next correct move
Auto Solve — solves the puzzle automatically
Day / Night — switches the visual theme
Rules — shows the game rules

🏁 Objective

Move all four entities:

Farmer
Wolf
Goat
Cabbage

from the left bank to the right bank safely.

The puzzle is completed only when all are successfully transported without the goat being eaten by the wolf or the cabbage being eaten by the goat.

🧪 Technologies Used

Python
Tkinter
Math module

No external libraries are required beyond Python’s standard library
📜 Reference Solution Path

The built-in solution path used by the program is:

Take Goat
Return Alone
Take Wolf
Bring Goat Back
Take Cabbage
Return Alone
Take Goat

This sequence is stored directly in the game engine and powers the hint and auto-solve functionality
🚀 Future Improvements

Possible future enhancements include:

BFS/DFS based dynamic solver
Difficulty modes
Sound effects
Score saving / leaderboard
Better responsive layout
Character selection or theme customization
