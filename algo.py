# coding=utf-8
import copy
import random
import typing
import pygame
import konstanten
import model


class MazeGenerator(object):
    def __init__(self, y_Achse: int, x_Achse: int, kantenlaenge: int):
        self.y_Achse: int = y_Achse
        self.x_Achse: int = x_Achse
        self.kantenlaenge: int = kantenlaenge
        self.startKy: int = random.randint(0, y_Achse - 1)
        self.startKx: int = random.randint(0, x_Achse - 1)
        self.maze = model.Maze(y_Achse, x_Achse, kantenlaenge)
        self.labyrinth = self.maze.labyrinth   
        self.spanning3: dict = {}
        self.stack = model.Stack()
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
       """ L??scht die entsprechende KantenwandTyp innrhalb der ??bergebenen Koordinate im Labyrinth.

        :param k: Die Koordinate dessen Kantenwand gel??scht werden soll.
        :type k:  Koordinate
        :param wandTyp: 'h'-Schl??ssel f??r horizontal oder 'v'-Schl??ssel f??r vertikal
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
    """Der Pathfinder berechnet und markiert den L??sungpfad von der akt. Position des Spielers bis zum Ziel."""
    def __init__(self, mazerator: MazeGenerator, player: model.Player, isDoPathFinder: bool = True):
        """
        Initialisiert alle Attribute der Klasse und ruft die Funktionen findPath() sowie solutionPath2Labyrinth() auf

        sofern isFindPath True ist. Bei False wird kein L??sungspfad gesucht und somit auch kein L??sungspfad im Labyrinth
        ??bertragen. Dieser Fall tritt ein, wenn der spanningTree angezeigt wird, den PathFinder.stack zu bef??llen.
        Das F??llen des stacks bewirkt das Zur??cksetzen der Felder im Labyrinth, die zuvor ein L??sungpfad oder
        MazeGenerator.spanningTree anzeigten, um ein erneutes Anzeigen des L??sungpfads oder spanningTree korrekt
        ausgeben zu k??nnen. Ohne zur??cksetzen der Felder sieht der Spieler die Reste des spanningTree, wenn dieser
        sich f??r die Anzeige eines L??sungspfad nach der Animation des spanningTree entscheidet.

        :param mazerator: Die MazeGenerator-Instanz mit der das Labyrinth generiert wurde.
        :type mazerator:  algo.MazeGenerator
        :param player:  Die Player-Instanz, welche die aktuelle Position des Spielers beinhaltet.
        :type player:   model.Player
        :param isDoPathFinder: True, wenn L??sungspfad berechnet werden soll, sonst False.
        :type isDoPathFinder:  bool
        """
        self.stack = model.Stack()  # der L??sungspfad
        if isDoPathFinder:
            self.validPath: dict = copy.deepcopy(mazerator.spanning3)
            self.labyrinth = mazerator.labyrinth
            self.player = player
            self.findPath()
            self.solutionPath2Labyrinth()

    def findPath(self) -> None:
        """ Berechnet den L??sungspfad auf Grundlage des Spannbaums."""
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
        """Weist jeder Koodinate des L??sungspfad dessen Koordinatenfeld (cell.rect) und Farbe (SOLUTIONPATHCOLOR) zu.

        Nach der Fertigstellung des L??sungspfads erstellt diese Funktion f??r die Koordinaten im L??sungspfad das
        grafische Feld pygame.Rect, welches bei der Ausgabe des Labyrinths als L??sungspfad angezeigt wird.
        Die Stack-Klasse speichert (referenziert) die Koordinaten der Klasse Koordinate in einer Liste ab, welche beim
        ??bertragen der Daten einfach normal nach dem First-in-First-out-Prinzip (FiFo, Queue) ausgelesen wird. Jedoch
        werden das aktuelle Spielerpositions-Feld sowie das Zielfeld nicht erzeugt und somit auch keine Farbe
        zugeordnet. Dies dient besonders bei sehr gro??en Labyrinths (100x100) zur besseren Orientierung, wo der Anfang
        und Ende im Labyrinth zu finden ist, zur Kontrolle des L??sungspfads an sich sowie als Nachweis, dass
        tats??chlich ein L??sungspfad existiert. Indirekt kann man damit auch nachweisen, dass alleine auf Grundlage des
        des self.validPaths, welches im Grunde genommen eine 1:1 Kopie des spanning3 ist, vor der Berechnung des
        L??sungspfads, beliebige L??sungspfade sich errechnen lassen, d.h. von einem beliebigen Punkt zu einem anderen
        beliebigen Punkt im Labyrinth, existiert in dem erstellten Labyrinth immer genau ein Pfad, welches durch das
        spanning3 errechnet werden kann.
        """
        for cell in self.stack.liste:
            cell.solutionMarker = self.calculateRect(cell)
            cell.solutionMarkerColor = konstanten.SOLUTIONPATHCOLOR

    def resetMarker(self) -> None:
        """ Setzt den solutionMarker der Koordinate-Instanz im L??sungspfad self.stack.liste zur??ck.

        Diese Funktion dient zum resetten des solutionMarkers der Koodinate-Instanzen, die als L??sungspfad in der
        self.stack.liste abespeichert sind, um einen neuen L??sungspfad mit der aktuelleren Position des Spielers
        anzeigen zu k??nnen. Die Ausgabe eines L??sungspfads erfolgt nur dann, wenn die Koordinate-Instanz in
        self.stack.liste im solutionMarker auch das entsprechende Koordinatenfeld beinhaltet (pygame.Rect). Anders
        ausgedr??ckt: Die Farbe eines Objekts kann nur dann gesehen werden, wenn das Objekt existiert. Das None gibt
        jedoch bei der Ausgabe des Labyrinths an, dass nichts im solutionMarker steht, was auf dem Bildschirm angezeigt
        werden kann.
        """
        for cell in self.stack.liste:
            cell.solutionMarker = None

    @staticmethod
    def calculateRect(k: model.Koordinate) -> pygame.Rect:
        """
        Berechnet ein pygame.Rect Feld f??r die Ausgabe des L??sungspfads und spanning3

        Die Berechnung unterscheidet sich ein wenig von der Berechnung innerhalb der Funktion Koordinate.rect. Das
        berechnete Feld hier ist etwas kleiner als das Feld aus Koordinate.rect, wodurch eine klare Unterscheidung
        zwischen L??sungspfad und Spieler-Weglauf gesehen werden kann.

        Bei Labyrinthgr????en wie 269*479 ist die Anzeige des L??sungspfads nur auf gro??en Monitoren nachvollziehbar, da
        der L??sungspfad nur durch ein Feld mit einem Pixel angezeigt wird.

        """
        x = konstanten.FENSTER_RAND_ABSTAND + k.x * k.laenge + (k.laenge / 4)
        y = konstanten.FENSTER_RAND_ABSTAND + k.y * k.laenge + (k.laenge / 4)
        width = k.laenge - (k.laenge / 2)
        height = k.laenge - (k.laenge / 2)
        return pygame.Rect(x, y, width, height)
