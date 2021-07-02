# coding=utf-8
import copy
import model
from typing import *
from model import *

class MazeGenerator(object):
    def __init__(self, y_Achse: int, x_Achse: int, kantenlaenge: int):
        self.y_Achse: int = y_Achse
        self.x_Achse: int = x_Achse
        self.kantenlaenge: int = kantenlaenge
        self.startKy: int  = random.randint(0, y_Achse - 1)
        self.startKx: int  = random.randint(0, x_Achse - 1)
        self.maze: Maze = model.Maze(self.y_Achse, self.x_Achse, kantenlaenge)
        self.labyrinth: List[List[model.Koordinate]] = self.maze.labyrinth
        self.spanning3: dict = {}
        self.stack: model.Stack = model.Stack()
        self.createWalls()
        self.createMaze(self.labyrinth[self.startKy][self.startKx])

    def createWalls(self) -> None:
        """
        Bildet den Anfangszustand des Labyrinths mit dem Kantennetzwerk.

        Die "Kanten" sind hier die Rechteckobjekte pygame.Rect,
        """
        for y in range(self.y_Achse + 1):
            for x in range(self.x_Achse + 1):
                vh_x = konstanten.FENSTER_RAND_ABSTAND + (x * self.kantenlaenge)
                vh_y = konstanten.FENSTER_RAND_ABSTAND + (y * self.kantenlaenge)
                if x < self.x_Achse:  # Bildung der horizontalen Kantendimension
                    self.labyrinth[y][x].kanten['h'] = pygame.Rect(vh_x, vh_y, self.kantenlaenge, konstanten.HOEHE)
                if y < self.y_Achse:  # Bildung der vertikalen Kantendimension
                    self.labyrinth[y][x].kanten['v'] = pygame.Rect(vh_x, vh_y, konstanten.HOEHE,self.kantenlaenge)

    def createMaze(self, aktuelZel: model.Koordinate) -> None:
        """ Generiert das Labyrinth nach dem iterativen Dept-First-Backtracking-Verfahren.

        Zur Hiflfe wurde folgendes PSeudoCode verwendet, die als Kommentar im Code angegeben sind: \n
        1.  Choose the initial cell, mark it as visited and push it to the stack
        2.  While the stack is not empty
                1. Pop a cell from the stack and make it a current cell
                2. If the current cell has any neighbours which have not been visited
                    1.  Push the current cell to the stack
                    2.  Choose one of the unvisited neighbours
                    3.  Remove the wall between the current cell and the chosen cell
                    4.  Mark the chosen cell as visited and push it to the stack
        PseudoCode Quelle:
        https://en.wikipedia.org/wiki/Maze_generation_algorithm#:~:text=in%20the%20area.-,Iterative%20implementation,-%5Bedit%5D
        :param aktuelZel: Der Startpunkt von wo aus die Generierung des Labyrinths beginnt.
        :type aktuelZel:  model.Koordinate
        """
        aktuelZel.isVisited = True  # 1.
        self.stack.push(aktuelZel)  # 1.
        while self.stack.isNotEmpty():  # 2.
            aktuelZel = self.stack.popp()  # type: model.Koordinate       # 2.1

            if (aktuelZel.y, aktuelZel.x) not in self.spanning3:
                self.spanning3[(aktuelZel.y, aktuelZel.x)] = []

            if aktuelZel.neighbours:  # 2.2
                self.stack.push(aktuelZel)  # 2.2.1
                nextCell_y, nextCell_x, kantenTyp = random.choice(aktuelZel.neighbours)  # 2.2.2
                aktuelZel.neighbours.remove((nextCell_y, nextCell_x, kantenTyp))

                if self.maze.isValid_and_isNotVisited(nextCell_y, nextCell_x): # 2.2
                    nxtZel = self.labyrinth[nextCell_y][nextCell_x]  # 2.2.2
                    # find out which direction it went, if...
                    if (nxtZel.y + nxtZel.x - aktuelZel.y - aktuelZel.x) > 0:
                        # ... right or down, then delete the wall kantentyp ("h" or "v") in nxtZel.kanten  
                        self.deleteWall(nxtZel, kantenTyp)  # 2.2.3
                    else: # ... left or up, then delete the wall kantentyp ("h" or "v") in aktuelZel.kanten
                        self.deleteWall(aktuelZel, kantenTyp)  # OR 2.2.3

                    self.spanning3[(aktuelZel.y, aktuelZel.x)].append([nxtZel.y, nxtZel.x])

                    if (nxtZel.y, nxtZel.x) in self.spanning3:
                        self.spanning3[nxtZel.y,nxtZel.x].append([aktuelZel.y, aktuelZel.x])
                    else:
                        self.spanning3[nxtZel.y,nxtZel.x] = [[aktuelZel.y, aktuelZel.x]]

                    nxtZel.isVisited = True  # 2.2.4
                    self.stack.push(nxtZel)  # 2.2.4

    def deleteWall(self, k: model.Koordinate, wandTyp: str) -> None:
       """ Löscht die entsprechende KantenwandTyp innrhalb der übergebenen Koordinate im Labyrinth.

        :param k: Die Koordinate dessen Kantenwand gelöscht werden soll.
        :type k:  Koordinate
        :param wandTyp: 'h'-Schlüssel für horizontal oder 'v'-Schlüssel für vertikal
        :type wandTyp: str
       """
       del self.maze.labyrinth[k.y][k.x].kanten[wandTyp]

    def getKoordinatenData(self) -> str:
        ausgabe: str = ""
        for y in range(self.y_Achse + 1):
            for x in range(self.x_Achse + 1):
                ausgabe += f"{self.labyrinth[y][x].getKoordinatenKantenDaten} "
            ausgabe += "\n"
        return ausgabe


class PathFinder(object):
    """Der Pathfinder berechnet und markiert den Lösungpfad von der akt. Position des Spielers bis zum Ziel."""
    def __init__(self, mazerator:MazeGenerator, player:model.Player, isDoPathFinder=True):
        """
        Initialisiert alle Attribute der Klasse und ruft die Funktionen findPath() sowie solutionPath2Labyrinth() auf

        sofern isFindPath True ist. Bei False wird kein Lösungspfad gesucht und somit auch kein Lösungspfad im Labyrinth
        übertragen. Dieser Fall tritt ein, wenn der spanningTree angezeigt wird, den PathFinder.stack zu befüllen.
        Das Füllen des stacks bewirkt das Zurücksetzen der Felder im Labyrinth, die zuvor ein Lösungpfad oder
        MazeGenerator.spanningTree anzeigten, um ein erneutes Anzeigen des Lösungpfads oder spanningTree korrekt
        ausgeben zu können. Ohne zurücksetzen der Felder sieht der Spieler die Reste des spanningTree, wenn dieser
        sich für die Anzeige eines Lösungspfad nach der Animation des spanningTree entscheidet.

        :param mazerator: Die MazeGenerator-Instanz mit der das Labyrinth generiert wurde.
        :type mazerator:  algo.MazeGenerator
        :param player:  Die Player-Instanz, welche die aktuelle Position des Spielers beinhaltet.
        :type player:   model.Player
        :param isDoPathFinder: True, wenn Lösungspfad berechnet werden soll, sonst False.
        :type isDoPathFinder:  bool
        """
        self.stack: model.Stack = model.Stack()  # der Lösungspfad
        if isDoPathFinder:
            self.validPath: dict = copy.deepcopy(mazerator.spanning3)
            self.labyrinth: List[List[Koordinate]] = mazerator.labyrinth
            self.player: model.Player = player
            self.findPath()
            self.solutionPath2Labyrinth()

    def findPath(self) -> None:
        """ Berechnet den Lösungspfad auf Grundlage des Spannbaums."""
        nextCell_y, nextCell_x = -1, -1
        self.stack.push(self.labyrinth[self.player.currentKy][self.player.currentKx])

        while (nextCell_y, nextCell_x) != (self.player.zielKy, self.player.zielKx):
            currentCell = self.stack.popp()
            validPathList = self.validPath[(currentCell.y, currentCell.x)]
            if validPathList:
                self.stack.push(currentCell)

                nextCell_y, nextCell_x = random.choice(validPathList)
                self.validPath[(currentCell.y, currentCell.x)].remove([nextCell_y,nextCell_x])
                self.validPath[(nextCell_y, nextCell_x)].remove([currentCell.y,currentCell.x])
                
                self.stack.push(self.labyrinth[nextCell_y][nextCell_x])

    def solutionPath2Labyrinth(self) -> None:
        """Weist jeder Koodinate des Lösungspfad dessen Koordinatenfeld (cell.rect) und Farbe (SOLUTIONPATHCOLOR) zu.

        Nach der Fertigstellung des Lösungspfads erstellt diese Funktion für die Koordinaten im Lösungspfad das
        grafische Feld pygame.Rect, welches bei der Ausgabe des Labyrinths als Lösungspfad angezeigt wird.
        Die Stack-Klasse speichert (referenziert) die Koordinaten der Klasse Koordinate in einer Liste ab, welche beim
        Übertragen der Daten einfach normal nach dem First-in-First-out-Prinzip (FiFo, Queue) ausgelesen wird. Jedoch
        werden das aktuelle Spielerpositions-Feld sowie das Zielfeld nicht erzeugt und somit auch keine Farbe
        zugeordnet. Dies dient besonders bei sehr großen Labyrinths (100x100) zur besseren Orientierung, wo der Anfang
        und Ende im Labyrinth zu finden ist, zur Kontrolle des Lösungspfads an sich sowie als Nachweis, dass
        tatsächlich ein Lösungspfad existiert. Indirekt kann man damit auch nachweisen, dass alleine auf Grundlage des
        des self.validPaths, welches im Grunde genommen eine 1:1 Kopie des spanning3 ist, vor der Berechnung des
        Lösungspfads, beliebige Lösungspfade sich errechnen lassen, d.h. von einem beliebigen Punkt zu einem anderen
        beliebigen Punkt im Labyrinth, existiert in dem erstellten Labyrinth immer genau ein Pfad, welches durch das
        spanning3 errechnet werden kann.
        """
        for cell in self.stack.liste:
            cell.solutionMarker = self.calculateRect(cell)
            cell.solutionMarkerColor = konstanten.SOLUTIONPATHCOLOR

    def resetMarker(self) -> None:
        """ Setzt den solutionMarker der Koordinate-Instanz im Lösungspfad self.stack.liste zurück.

        Diese Funktion dient zum resetten des solutionMarkers der Koodinate-Instanzen, die als Lösungspfad in der
        self.stack.liste abespeichert sind, um einen neuen Lösungspfad mit der aktuelleren Position des Spielers
        anzeigen zu können. Die Ausgabe eines Lösungspfads erfolgt nur dann, wenn die Koordinate-Instanz in
        self.stack.liste im solutionMarker auch das entsprechende Koordinatenfeld beinhaltet (pygame.Rect). Anders
        ausgedrückt: Die Farbe eines Objekts kann nur dann gesehen werden, wenn das Objekt existiert. Das None gibt
        jedoch bei der Ausgabe des Labyrinths an, dass nichts im solutionMarker steht, was auf dem Bildschirm angezeigt
        werden kann.
        """
        for cell in self.stack.liste:
            cell.solutionMarker = None

    @staticmethod
    def calculateRect(k: Koordinate) ->pygame.Rect:
        """
        Berechnet ein pygame.Rect Feld für die Ausgabe des Lösungspfads und spanning3

        Die Berechnung unterscheidet sich ein wenig von der Berechnung innerhalb der Funktion Koordinate.rect. Das
        berechnete Feld hier ist etwas kleiner als das Feld aus Koordinate.rect, wodurch eine klare Unterscheidung
        zwischen Lösungspfad und Spieler-Weglauf gesehen werden kann.

        Bei Labyrinthgrößen wie 269*479 ist die Anzeige des Lösungspfads nur auf großen Monitoren nachvollziehbar, da
        der Lösungspfad nur durch ein Feld mit einem Pixel angezeigt wird.

        """
        x = konstanten.FENSTER_RAND_ABSTAND + k.x * k.laenge + (k.laenge / 4)
        y = konstanten.FENSTER_RAND_ABSTAND + k.y * k.laenge + (k.laenge / 4)
        width = k.laenge - (k.laenge / 2)
        height = k.laenge - (k.laenge / 2)
        return pygame.Rect(x, y, width, height)
