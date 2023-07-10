# Hasami Shogi

This project implements a game of 
[Hasami Shogi](https://en.wikipedia.org/wiki/Hasami_shogi#Variant_1) using 
PyGame. There are 2-player, 1-player (Player vs AI), and 0-player (AI vs AI) 
variants.

### Running the Program

To run the program, Python version 3.9 or higher is required. Download or 
clone the repo, then run the file main.py. Follow the prompts in the command 
line, and a game will begin.

### Playing the Game
In 1 or 2-player mode, you can move pieces by clicking on the desired piece 
to select it, then clicking on the destination square. Click off of the selected
piece to deselect it. Capture enemy pieces by positioning your pieces to 
"sandwich" one or more of theirs in a row, or by trapping one of their 
pieces in a corner.

### AI Opponent
The AI opponent uses the 
[Minimax algorithm](https://en.wikipedia.org/wiki/Minimax) to simulate all 
possible moves up to a depth of 3 moves ahead. It chooses the move that will 
maximize its chance's of winning, given that its opponent will seek to 
minimize its chances of winning.  

The speed of the algorithm is improved using
[Alpha-Beta Pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning). 
This technique greatly reduces the number of branches the algorithm will 
need to evaluate. This is further improved using the move-ordering technique,
where moves that are more likely to find the best evaluation are simulated 
first.

Can you beat the AI?

### Challenges
The biggest challenge with this project has been implementing the AI in an 
efficient manner. On average, each player has about 60 available moves, 
meaning that the number of moves to check is multiplied by 60 for each level 
of depth to look ahead. Much of my work on this project has been to optimize 
the algorithms and data structures used by the AI to track game state. 

### Next Steps
I intend to continue optimizing the AI to start generating moves beyond a 
depth of 3. I am also continuing to refactor the code to be cleaner, which 
I've found can also help with optimization. This was one of the first 
programs I wrote early in the OSU Computer Science curriculum, and I've 
learned a lot in the past two years. As I continue to learn, I will come 
back here to update and improve the program.
