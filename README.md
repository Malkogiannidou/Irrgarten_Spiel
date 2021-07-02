# MazeGame_MazeSolver_MazeGenerator
MazeGame, Maze-Generator, Maze-Solver  

Is a minimalistic Maze-Game with random starting and end point.  It will work only on windows, 
but works also in OSX or linux, if you manually type your local screen resolution in the module 
konstanten.py at line 7:    
SCREENSIZE = (1920,1080) # and put a comment [#] at the start of line 3 and 5   

Dependency:  
Install python 3.8 or highter and the pygame-Modul 2.0.1 or newer 

The Game can be started by navigating to the games directory and by typing following commands in the pycharm terminal: 

1) python mazespiel.py   
2) python mazespiel.py 10 20   
3) python mazespiel.py -y 20 -x 30  or python mazespiel.py --yaxis 20 --xaxis 30   
4) python mazespiel.py -x 30 -y 20  or python mazespiel.py --xaxis 30 --yaxis 20   
Starting directly the game without printing the maze in the console:     
5) python mazespiel.py -y 40 -x 50 -gui    
For help:    
python mazespiel.py -h              or python mazespiel.py --help   

If one didn't start directly into the game, but used above parameterized execution of the game
then the programm starts in the console and prints the menu will be shown.   

If parametrized start of the game:    
please type [v] and press Return.  

If not parameterized:  
  Option 1) type the axis for x and y by typing:  20 30  or  60x70  
            press Return      
  Option 2) press Return and type for:       
      xaxis: 100   
      press Return   
      yaxis: 99    
      press Return     
      
Programm validates any number given. Theoretically the used iterative dept-first-backtracking algorithm 
could calculate an infinite "perfect" maze, but we restricted the calculation depending on your local screen
resolution devided by 4 pixel.    

As an example the xaxis can go up to 479 fields and the yaxis up to 269 at FullHD (1920*1080) resolution.     

After choosing the menu option the maze will be printed out in the console. If the maze size ist beween
10x10 to 30x30 (dependent on your local screen resolution) then you can compare the output also with the 
graphical output and you won't see much differene apart from 
the color and field like the starting and ending point.    

A new window will appear eighter in window mode or full-screen mode depending on how high your fields are. 
If in full-screen mode, you have to click with the mouse anywhere in the screen.   

On the upper left corner (depending on the maze-size) the menu is shown, which disappears if typed any key. 
To play the game use the arrow keys or [w, a, s, d]. Your goal is to get to the pinkish end point ;-). 
Obviously you can't cross any walls or fallout of the maze.   

Menu options can be pressed at any time during the game:      
**[F1]** Will calculate a solution path from your current position. If one chose a maze as big as 479x269 then it might 
     take 1-2 Seconds untill you see the solution path. Is also a switch for not showing the solution Path.  
     
**[Return]** Will animate the spanning tree and therefore also how the maze got created. Speed of the animation depends on the 
         size of the maze. Is also a switch for not showing the animation.  

**[g]** For randomly choosing new start and end point. If solution path was shown before, it will choose new start & end point
    and afterward shows the solution path.  
    
**[k]** It shows that we used only 2 walls (2 edges instead of 4) for each field to build the grid of walls in the maze. The 
    generator (MazeGenerator.createMaze in the module algo.py) "walks" through the maze and destroy the wall which is between
    two fields. Uses backtracking if all neighbours of the particular field were already visited upt to the point where it 
    gets a field which has 1-3 neighbours which are not yet visited... just press [Return] to see the maze creation. 
    Is a switch.  

**[m]** Shows the menu. Is a switch. 

**[q] or [Esc] or [ALT + F4]** or in window mode pressing the {X}-Button on the window will close the game. 

Game closes also by reaching the goal. After that the statistics will be shown in the console like how much time it took 
to reach the goal or quiting the game. How many times you pressed [g] to change start and end field. 

If the goal was reached than the statistics will make more sense after the above one, as it will give some clues about 
your performance in context to the solution path size. If quited manually than it will show the total amount of you steps. 
and then the valid steps and invalid steps (the one with headon against the wall) and the solution path size. 

After that the maze is printed out in the console again, but this time with the solution path in it. 
At the end the console menu gets printed out. Choose [q] and press [Return] to exit the game. 

Ending the game, if started parameterized via [-gui] will also exit the game it self. 

