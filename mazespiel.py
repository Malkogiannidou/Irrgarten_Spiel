# coding=utf-8
# Frankfurf University of Applied Sciences - Betriebssystem und Rechnernetze-Werkstück A7, Prof.Dr.Baun 
# Authoren: Stella Malkogiannidou, Amaal Mohamed, Samira Hersi
# Datum: 28.06.21
import argparse
import copy
import pygame
import pygame.freetype
import pygame.surface
import re
import sys
import time
from typing import *

import algo
import konstanten
import model


class MazeSpiel:
    """Startet das Maze-Spiel"""
    def __init__(self, y_Achse: int, x_Achse: int, maze_generator: algo.MazeGenerator,
                 player: model.Player, screentype: int):
        # Pygame init, Anzeigemodus m. ggf. Größenberechnung, Bildschirmfläche, FPS
        pygame.init()
        self.flags = screentype                                 # type: int
        self.screenSize = konstanten.SCREENSIZE                 # type: Tuple[int, int]
        if self.flags == pygame.locals.RESIZABLE:                             # DAS ↓ IST FALSCH! hier müsste...
                                                             # ...normalerweise die ↓ berechnete kantenlaenge stehen.
            self.screenSize =(2 * konstanten.FENSTER_RAND_ABSTAND + x_Achse * konstanten.LAENGE + konstanten.HOEHE),\
                             (2 * konstanten.FENSTER_RAND_ABSTAND + y_Achse * konstanten.LAENGE + konstanten.HOEHE)
        self.screen = pygame.display.set_mode(self.screenSize, self.flags,32)
        pygame.display.set_caption('MazeGame')
        self.framesPerSecond = x_Achse if x_Achse > y_Achse else y_Achse     # type: int
        # Achsenwerte
        self.xAchse, self.yAchse = x_Achse, y_Achse             # type: int, int

        # Labyrinth, Wandfarbe, Spannbaum (spanning3, sp3)
        self.mazerator:algo.MazeGenerator = maze_generator
        self.labyrinth:List[List[model.Koordinate]] = maze_generator.labyrinth
        self.kantenfarbe:Tuple[Tuple[int, int, int], Tuple[int, int, int]] = (konstanten.WALLCOLOR_1, konstanten.WALLCOLOR_1) 
        self.spanning3_1stKey = maze_generator.startKy, maze_generator.startKx  # type: Tuple[int, int]
        self.sp3_ykey, self.sp3_xkey, self.sp3copy = 0,0,None   # type: int,int, None

        # Player, Index-Modifikatoren für Spielerbewegungsrichtung, pathFinder init
        self.player:model.Player     = player
        self.startKy, self.startKx = self.player.currentKy, self.player.currentKx    # type: int, int
        self.directions: Dict[str, Tuple[int, int]] = {'right':(0, 1), 'left':(0, -1), 'down':(1, 0), 'up':(-1, 0)}
        self.pathFinder = None                                  # type: None or algo.PathFinder

        # Boolean-Switch, Counter-Variablen und solutionSize (Lösungspfadlänge) init
        self.isShowMenu, self.isRunning = True, True            # type: bool, bool
        self.isShowSolutionPath, self.isShowSpaning3, self.is2farbig = False, False, False
        self.totalMoves, self.invalidMoves  = 0, 0              # type: int, int
        self.solutionSize, self.gTasteCount = 0, 0              # type: int, int

        # Menüvorbereitung, Überschreiben der entsprechenden Marker der jeweiligen Koordinaten-Instanzen
        self.menuText_ImageList = self.initMenu()  # type:  List[pygame.surface.Surface]
        self.markStart_Ziel(self.player.currentKy, self.player.currentKx, konstanten.STARTCOLER)
        self.markStart_Ziel(self.player.zielKy, self.player.zielKx, konstanten.ZIELCOLER)

    @staticmethod
    def initMenu() -> List[pygame.surface.Surface]:                                                 # Menü-Init
        """
        Vorberetiung für die spätere Anzeige des Menüs durch das Rendern der Menüzeilen zu einem Bild.

        Rendert jede Zeile Menütext als Bild und speichert das Ergebnis in einem Array text_Images ab,
        welches zurück gegeben wird.
        :return: Das Array mit den gerenderten Menütext-Zeilen
        :rtype: List[Union[Surface, SurfaceType]]
        """
        font_24 = pygame.font.SysFont('consolas.ttf', 24)
        font_20 = pygame.font.SysFont('consolas.ttf', 20)
        titleColor, textColor, infoColor = konstanten.ROT, konstanten.GRUENNEON, konstanten.BLAUNEON
        text_Images = [ font_24.render(6*" "+'M a z e G a m e  [ m ] E N Ü      ',
                                                                    True,titleColor),
            font_24.render('   Pfeiltasten Pfeiltasten: < ^  > v ',True, textColor),
            font_24.render(
                '                             oder mit: a x d s ', True, textColor),
            font_24.render(
                '                  Lösungspfad: F1          ',     True, textColor),
            font_24.render('                Spanning Tree: Enter    ',
                                                                    True, textColor),
            font_24.render(' Start-Ziel Neuvergabe: g             ',True, textColor),
            font_24.render('     Wandfarben-Switch: k             ',True, textColor),
            font_24.render('               Spiel beenden: q, Esc    ',
                                                                    True, textColor),
            font_20.render('     Start, Ziel? Evtl. hinter Menü?          ',
                                                                    True, infoColor)]
        return text_Images

    def markStart_Ziel(self, ky: int, kx: int, farbe: Tuple[int, int, int]) -> None:
        """
        Überschreibt den Feldmarker im Labyrinth mit pygame.Rect-Objekt, und speichert dessen Farbe ab.

        Zuvor stand noch ein String für Start und Zielfeld. Ausgabe des Labyrinths das Start- und
        Zielfeld durch die entsprechend angezeigte Farbe in Koordinate.markerColor zu markieren.

        :param ky: Die Zeile in der dieses Koordinatenfeld im 2D-Array labyrinth sich befindet.
        :type ky: int
        :param kx: Die Spalte in der diese Koordinatenfeld im 2D-Array labyrinth sich befindet
        :type kx: int
        :param farbe: Die Farbe entweder als RGB-Tupel oder entsprechende Konstante
        :type farbe:  Tuple[int, int, int]
        """
        self.labyrinth[ky][kx].marker = self.labyrinth[ky][kx].rect
        self.labyrinth[ky][kx].markerColor = farbe

    def run(self) -> None:                                            # Hauptschleife Spiel
        """ Ist die Hauptschleife des Spiels in der graphischen Ausgabe via Pygame

        Durch die Haupschlefe können Änderungen im Lybrinth nachvollziehbar
        graphisch ausgegeben werden. \n
        Es werden u.a. die pygameEvents geprüft, das Labyrinth ausgegeben, das Menü, isShowMenu True
        ist und die Animation des Spannbaums. Bei der Animation ist jedoch noch die besonderheit,
        dass diese while-Hauptschleife bereits ein Teil des Algorithmus der Animation ist, womit der
        Algo den Spannbaum "durchiteriert", indem dieser in do_showSpanningTree für jeden Durchlauf
        einen neuen Schlüssel setzt.  \n
        Anschließend erfolgt die eigentliche Anzeige auf der Anzeigefläche (Fenstermodus) oder gesamten
        Bildschirm (Vollbildmodus). Um die Prozessorlast zu veringern, kann die Angabe clock.tick(FPS)
        dazu beitragen, indem eine bestimmte Grenze für die Berechnung der Bilder pro Sekunde
        gesetzt wird, wodurch die CPU-Last sich verringert (Standard ist 60FPS, Gamer 140FPS). \n
        Für jeden Schleifendurchlauf prüft das Programm, ob der Spieler das Zielfeld erreicht hat.
        Wenn ja wird das Spiel beendet und die Auswertung in der Konsole ausgegeben. Wenn nicht,
        dann setzt das Spiel einfach fort, es sei denn der Spieler löst ein Ereignis aus,
        wodurch das Spiel vorzeitig beendet wird.
        """
        isSuccess, playerTimer = False, time.time()     # type: bool, float
        clock = pygame.time.Clock()                                 # FPS-Begrenzer
        while self.isRunning:
            self.screen.fill(konstanten.BGCOLOR)         # reset screen auf BGCOLOR

            for ereignis in pygame.event.get():               # Benutzerinteraktion
                self.do_pygameEvents(ereignis)

            self.do_drawLabyrinth()                             # Zeichne Labyrinth

            if self.isShowMenu:                                     # Zeige Menü an
                self.do_drawMenu()

            if self.isShowSpaning3:  # Nutzt while Schleife zum spanning3 animieren
                self.do_showSpanningTree(clock)

            pygame.display.flip()         # Zeige gezeichnete Objekte auf screen an
            clock.tick(self.framesPerSecond)
                                 # Sobald Spieler Ende erreicht wird Spiel beendet.
            if self.player.getPos() == (self.player.zielKy, self.player.zielKx):
                playerTimer = time.time() - playerTimer  # type:float
                isSuccess = True                         # type:bool
                self.isRunning = False                   # type:bool

        self.do_printGameMetrics(isSuccess, playerTimer)        # Gebe Auswertung aus
        pygame.quit()                                              # Beendet Pygame

    def do_pygameEvents(self, ereignis: pygame.event.Event) -> None:  # Benutzerinteraktion
        """ Benutzerinteraktion durch den Benutzer initiiert durch drücken der Tastatur Tasten.

        Jenachdem welche Tasten der Spielter drückte, verhält sich das Spiel entsprechend.

        Der Spieler kann folgende Tasten drücken:\n
        - '← ↑ → ↓' Pfeiltasten oder
        - 'a w d s' zur Steuerung im Labyrinth.
        - F1,um den Lösungspfad anzuzeigen,
        - Return-Taste für die Animation des self.spanning3,
        - g, um Start und Ziel neu zu vergeben,
        - k, um zwischen zweifarbige und einfarbige Wände zu wechseln,
        - m, um das Menü anzuzeigen und
        - q, oder
        - ESC, um das Spiel vorzeitig zu beenden.

        :param ereignis: Das Ereignis, welches in Pygame passiert, beim drücken von Tasten, Mouse etc.
        :type ereignis: pygame.event.Event
        """
        if ereignis.type == pygame.constants.QUIT:                       # Fenster "X" via Maus
            self.isRunning = False                   # oder Alt+F4 zum SpielBeenden
        elif ereignis.type == pygame.KEYDOWN:
            # Alternatives vorzeitiges Beenden des Spiels Spielsteuerung
            if ereignis.key == pygame.K_q or ereignis.key == pygame.K_ESCAPE:  self.isRunning = False

            elif ereignis.key == pygame.K_RIGHT or ereignis.key == pygame.K_d: self.on_keyEvent('right')

            elif ereignis.key == pygame.K_DOWN or ereignis.key == pygame.K_s:  self.on_keyEvent('down')

            elif ereignis.key == pygame.K_LEFT or ereignis.key == pygame.K_a:  self.on_keyEvent('left')

            elif ereignis.key == pygame.K_UP or ereignis.key == pygame.K_w:    self.on_keyEvent('up')

            elif ereignis.key == pygame.K_F1:              # Lösungspfad Aktion
                self.isShowSolutionPath = not self.isShowSolutionPath  # type:bool
                self.isShowSpaning3 = False                            # type:bool
                self.on_keyEvent_F1()

            elif ereignis.key == pygame.K_g: # Neuvergabe Start und Ziel zufällig
                self.on_keyEvent_g()
                self.gTasteCount += 1

            elif ereignis.key == pygame.K_RETURN:  # Animation Spannbaum Aktion
                if    self.pathFinder:  self.pathFinder.resetMarker()
                else: self.pathFinder = algo.PathFinder(self.mazerator,self.player,False)  # type: algo.PathFinder

                self.sp3copy = copy.deepcopy(self.mazerator.spanning3)        # type: dict
                self.sp3_ykey, self.sp3_xkey = self.spanning3_1stKey          # type: int, int
                self.isShowSpaning3 = not self.isShowSpaning3                 # type: bool

            elif ereignis.key == pygame.K_k: self.on_keyEvent_k() #Switch Kantenfarbe
            elif ereignis.key == pygame.K_t: print("\nSpannbaum-Daten:\n ",self.mazerator.spanning3,"\n")
            elif ereignis.key == pygame.K_m: self.isShowMenu = not self.isShowMenu      # type: bool
            if   ereignis.key != pygame.K_m:  self.isShowMenu = False                    # type: bool

    def do_drawLabyrinth(self) -> None:                                                  # Zeichne Labyrinth
        """  Zeichnet das Labyrinth auf die Anzeige self.screen.

        Zeichnet für jede model.Koordinaten-Instanz:\n
        1) zuallerst das marker.Feld (Start, Ziel, aktuelle
        Spielerposition), sofern darin ein pygame.Rect-Objekt existiert. Als nächstes sofern   \n
        2) self.isShowSolutionPath oder self.isShowSpaning3 True ist und Rect-Objekt in solutionMarker
        existiert, entweder den Lösungspfad oder die Animation des Spannbaums.\n
        3) Zum Schluss die horizontalen und/oder vertikalen Kanten, sofern Schlüssel "h" und oder "v" in
        kanten Dictionary vorkommt.
        """
        for row in range(self.yAchse + 1):                       # +1? Zur Anzeige des unteren Rands
            for column in range(self.xAchse + 1):                                 # +1? rechter Rand
                k_instanz = self.labyrinth[row][column]              # type: model.Koordinate

                if k_instanz.marker:                    # Feld für Spielverlauf, akt. Position, Ziel
                    pygame.draw.rect(self.screen, k_instanz.markerColor, k_instanz.marker)
                                                                    # für Lösungspfad oder Spannbaum
                if (self.isShowSolutionPath or self.isShowSpaning3) and k_instanz.solutionMarker:
                    pygame.draw.rect(self.screen,k_instanz.solutionMarkerColor, k_instanz.solutionMarker)

                if 'h' in k_instanz.kanten:                                       # horizontale Wand
                    pygame.draw.rect(self.screen, self.kantenfarbe[column % 2], k_instanz.kanten['h'])

                if 'v' in k_instanz.kanten:                                         # vertikale Wand
                    pygame.draw.rect(self.screen, self.kantenfarbe[column % 2], k_instanz.kanten['v'])


    def do_drawMenu(self) -> None:
        """  Gibt das Menü aus, welches aus mehreren Zeilen besteht.

        Damit das Labyrinth unter dem Menü nicht zu sehen ist, wird zuvor ein Rechteck mit der
        Hintergrundfarbe des Labyrinths gezeichent und darauf das Textbild der jeweiligen Menüzeile.
        """
        x, y = 30, 40            # type: int, int
        for textImage in self.menuText_ImageList:
            pygame.draw.rect(self.screen, konstanten.BGCOLOR, pygame.Rect(x,y,textImage.get_rect().w,textImage.get_rect().h))
            self.screen.blit(textImage, (x, y))
            y += 16

    def do_showSpanningTree(self, clock: pygame.time.Clock())-> None:
        """ Führt die Animation der Kopie sp3copy des Spannbaums self.mazerator.spanning3 durch.

        Übergeben wird noch das clock-Objekt, womit die Bilder-Pro-Sekunde gesetzt werden, wodurch die
        Aneinanderreihung (der Aufruf dieser Funktion) insgesammt zu dem Effekt einer Animation führen.

        :param clock:  Das Objekt, welches die Zeit misst, um die Bilder pro Sekunde zu begrenzen.
        :type clock:  pygame.time.Clock()
        """
        if self.sp3copy[self.sp3_ykey, self.sp3_xkey]:
            k: model.Koordinate = self.labyrinth[self.sp3_ykey][self.sp3_xkey]

            if not k.solutionMarker:
                k.solutionMarker = k.rect
                self.pathFinder.stack.push(k)
                k.solutionMarkerColor = konstanten.GENERATOR_COLOR
            else:
                k.solutionMarkerColor = konstanten.BACKTRACKER_COLOR

            self.sp3_ykey, self.sp3_xkey = self.sp3copy[self.sp3_ykey, self.sp3_xkey].pop()

            pygame.display.update(pygame.draw.rect(self.screen, k.solutionMarkerColor, k.solutionMarker))
            if 'h' in k.kanten:  # horizontale Wand
                pygame.display.update(pygame.draw.rect(self.screen, self.kantenfarbe[0], k.kanten['h']))
            if 'v' in k.kanten:  # vertikale Wand
                pygame.display.update(pygame.draw.rect(self.screen, self.kantenfarbe[0], k.kanten['v']))
            clock.tick(self.framesPerSecond)

    def do_printGameMetrics(self, isSuccess: bool, playerTimer: float)-> None:  # Auswertung
        """  Gibt die Spieler-Auswertungen aus wie Spieldauer, Schrittzähler, Lösungspfadlänge etc.

        :param isSuccess:  True, falls Spiel erfolgreich beendet wurde, sonst False.
        :type isSuccess:   bool
        :param playerTimer:  Die Dauer des Spiels in Sekunden.
        :type playerTimer:  float
        """
        self.player.setPos(self.startKy, self.startKx)
        self.isShowSolutionPath = True  # ← damit Lösungspfad in on_keyEvent_F1 überhaupt berechnet werden kann,...
        self.on_keyEvent_F1()           #...um den originalen Lösungspfad-Länge self.solutionSize zu erhalten.

        validMove    = self.totalMoves - self.invalidMoves
        validquote   = 0 if validMove == 0 else validMove * 100 / self.totalMoves
        invalidquote = 0 if self.invalidMoves == 0 else self.invalidMoves * 100 / self.totalMoves
        totalquote   = 0 if not isSuccess else self.solutionSize * 100 / self.totalMoves

        if isSuccess:
            print(konstanten.AUSWERTUNG_MSG.format('{:6.2f}'.format(playerTimer), "erfolgreich", self.gTasteCount))
        else:
            playerTimer = time.time() - playerTimer
            print(konstanten.AUSWERTUNG_MSG.format('{:6.2f}'.format(playerTimer),"vorzeitig", self.gTasteCount))

        print(konstanten.SOLUTION_MSG.format(self.totalMoves, validMove,'{:5.2f}'.format(validquote),
                                             self.invalidMoves,'{:5.2f}'.format(invalidquote),
                                             self.solutionSize,'{:5.2f}'.format(totalquote)))

    def on_keyEvent(self, direction: str)-> None: # Prüfung Bewegungsrichtung des Spielers
        """   Prüft, ob der Spieler in das Feld der gewünschte Bewegungsrichtung wechseln darf.

        Falls ja, wird neue Position des Spieler gesetzt. Für das Feld das pygame.Rect-Objekt
        berechnet und die Farbe auf VALIDMOVECOLOR gesetzt. Die alte Position erhält die Farbe
        PLAYERPATHCOLOR.\n
        Falls nein, dann ändert sich die Farbe des aktuellen Feldes zu INVALIDMOVECOLOR.

        :param direction: Die Richtung der Taste entsprechend: 'right",'left','up','down'
        :type direction: str
        """
        self.isShowSpaning3, self.isShowSolutionPath = False, False     # type: bool, bool
        self.totalMoves += 1                           # type: int
        mody, modx = self.directions[direction]        # type: int, int
        yvon, xvon = self.player.getPos()              # type: int, int
        ynach:int = yvon + mody
        xnach:int = xvon + modx

        if self.player.isDirectionValid(yvon, xvon, ynach, xnach):
            self.labyrinth[yvon][xvon].markerColor = konstanten.PLAYERPATHCOLOR
            self.labyrinth[ynach][xnach].marker = self.labyrinth[ynach][xnach].rect
            self.labyrinth[ynach][xnach].markerColor = konstanten.VALIDMOVECOLOR
            self.player.setPos(ynach, xnach)
        else:
            self.labyrinth[yvon][xvon].markerColor = konstanten.INVALIDMOVECOLOR
            self.invalidMoves += 1

    def on_keyEvent_F1(self) -> None:                              # Berechne Lösungspfad
        """  Berechnet den Lösungspfad, sofern isShowSolutionPath True ist.

        Setzt den solutionMarker der Koordinateninstanzen zurück, die im Pathfinder.stack vorkommen.
        Danach wird der Lösungsweg von der aktuellen Position des Spielers neu berechnet.
        """
        if self.isShowSolutionPath:
            if self.pathFinder:                  # reset alten Lösungspfad
                self.pathFinder.resetMarker()    # oder spanning3 in solutionMarker
            self.pathFinder = algo.PathFinder(self.mazerator, self.player)
            self.solutionSize = self.pathFinder.stack.size - 1

    def on_keyEvent_g(self) -> None:                              # Neuvergabe Start / Ziel
        """ Vergibt neues zufälliges Start- und Ziel-Feld

        Die Funktion wird erst aufgerufen, wenn der Spieler die Taste "g" drückt und loslässt (KEYUP).

        Es werden sowohl der Koordinate.marker wie auch der Koordinate.solutionMarker zurück gesetzt, um
        evtl.Spielerwegverlauf und Lösungspfadfelder zu löschen, da auch durch die erneute Zuweisung
        eines neuen Player das Start und Zielfeld neu genertiert werden. Anschließend wird noch der
        Marker für das Start und Zielfeldgesetzt, sodass der Spieler einen neuen Startpunkt und
        Zielpunkt in der grafischen Ausgabe sieht und direktweiter spielen kann. Falls der Spieler
        zuvor gespielt hatte, wird dessen Wegverlauf, Start- und Zielfeld und der durch das
        zurücksetzen des Koodrinate.marker und

        """
        self.isShowSpaning3 = False
        for zeile in range(self.yAchse):       
            for spalte in range(self.xAchse):
                self.mazerator.labyrinth[zeile][spalte].marker = None
                self.mazerator.labyrinth[zeile][spalte].solutionMarker = None

        self.player: model.Player = model.Player(self.yAchse, self.xAchse, self.mazerator.spanning3)
        self.startKy, self.startKx = self.player.currentKy, self.player.currentKx        # type: int, int
        self.markStart_Ziel(self.player.currentKy, self.player.currentKx, konstanten.STARTCOLER)
        self.markStart_Ziel(self.player.zielKy, self.player.zielKx, konstanten.ZIELCOLER)
        self.on_keyEvent_F1()

    def on_keyEvent_k(self) -> None:
        """ Switcht zwischen 2-Farbige (abwechselnd von Spalte zu Spalte) oder einfarbige Kantenwände im Labyrinth.

        Die Funktion wird erst aufgerufen, wenn der Spieler die Taste "k" drückt.
        """
        self.is2farbig: bool = not self.is2farbig
        if self.is2farbig:
            self.kantenfarbe: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = (konstanten.WALLCOLOR_1, konstanten.WALLCOLOR_2)
        else:
            self.kantenfarbe: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = (konstanten.WALLCOLOR_1, konstanten.WALLCOLOR_1)


class Konsole(object):
    """Hauptprogramm des Spiels für Achsenwert-Eingabe, Konsolen-Labyrinth-Ausgabe & Maze-Spiel-Start

    Via parametrisierten Start kann auch direkt das Spiel gestartet werden, ohne Konsolenausgbe des
    Labyrinths. Allerdings kann der Spieler nur eine "Runde" spielen und muss anschließend wieder das
    Programm starten. Mit dem normalen paramentrisierten Start ohne [-gui] wird die Konsole().run()
    ausgeführt und nach dem Ende Spiels, kann der Benutzer erneut neue Achsenwerte oder die gleichen
    wie in der vorigen Runde eingegebenen Achsenwerte das Spiel erneut startet, ohne dass das Programm
    beendet wird. Zum Beenden des Programms muss der Spieler in der Konsole bei der Benutzereingabe [
    q] eingeben.
    """
    def __init__(self, yAchse: int = 10, xAchse: int = 10):
        self.yAchse: int = yAchse
        self.xAchse: int = xAchse
        self.kantenlaenge: int = konstanten.LAENGE
        self.screentype: int = konstanten.SCREENTYPE
        self.mazerator = None  # type: None or  algo.MazeGenerator
        self.running, self.debug = True, False  # type: bool, bool

    def run(self) -> None:                                          # Hauptschleife Konsole
        """  Konsole-Hauptschleife: Eingabe der Achsenwerte, MazeGenerator, Player, startet MazeSpiel

        Ruft die Funktion setXYachsen auf, um das Menü auszugeben und Die Benutzereingabe entgegen zu
        nehemn. Prüft die Eingabe des Spielers auf Fehler und anschließend Validierung. Bei der
        Validierung wird geprüft, ob Spieler mindestns 10 und höchstens maximal in Abhängigkeit der
        lokalen Auflösung berechnete Feldanzahl der jeweiligen Achse angegeben hat. Des Weiteren wird
        in Abhängigkeit der Achsenwerte und der lokalen Auflösung die Kantenlänge einer Wand im
        Labyrinth für die spätere graph. Ausgabe berechnet und der Algorihtmus entscheidet,
        ob das Spiel im Fenstermodus oder Vollbildmodus angezeigt wird.

        Mit dem Aufruf der Klasse MazeGenerator erstellt das Programm einen "perfect" Maze.
        Durch das instanziieren eines Players, werden Start- und Ziel-Feld zufällig ausgewählt. Im
        Labyrinth an der entsprechenden Stelle mit "PLAY" und "END " markiert und anschließend erfolgt
        die Ausgabe des Labyrinths in der Konsole mit Angaben zu Dauer für die Maze-Berechnung sowie
        Berechnung des Ausgbestrings des Labyrinths.

        Anschließend erfolgt der Start des Spiels durch den Aufruf MazeSpiel.
        Nach dem Ende des Spiels gibt das Programm das Labyrinth mit dem markierten Lösungsweg aus.

        Danach wird das Menü ausgegeben. Das Programm kann mit der Eingabe q beendet werden.
        :rtype: None
        """
        while self.running:
            # M E N U  A U S G A B E  →  A C H S E N  I N P U T
            # → V A L I D I E R U N G → Wandlängenberechnung für die graph. Ausgabe
            self.setXYachsen()
            if not self.running:
                break

            # L A B Y R I N T H   E R S T E L L U N G
            startTimeToCreate: float = time.time()
            self.mazerator: algo.MazeGenerator = algo.MazeGenerator(self.yAchse, self.xAchse, self.kantenlaenge)

            # Zeitdauer zum Generieren und Auswahl der Zeiteinheit
            timeToCreateMaze: float = time.time() - startTimeToCreate
            mazeCreationTime: float = (timeToCreateMaze * 1000) if (timeToCreateMaze < 1) else timeToCreateMaze
            mazeCreationTimeUnit: str = "Millisekunden" if (timeToCreateMaze < 1) else "Sekunden"

            # P L A Y E R  I N S T A N Z I I E R U N G + Start/Ziel Markierung
            player: model.Player = model.Player(self.yAchse, self.xAchse, self.mazerator.spanning3)
            labyrinth: List[List[model.Koordinate]] = self.mazerator.labyrinth
            labyrinth[player.currentKy][player.currentKx].marker = "PLAY"
            labyrinth[player.zielKy][player.zielKx].marker = "END "

            # L a b y r i n t h - A u s g a b e  a l s  D a t e n
            if self.debug: print(f"{self.mazerator.getKoordinatenData()}\n\n")

            # K O N S O L E N - A U S G A B E - L A B Y R I N T H
            print(f" Labyrinth {self.yAchse, self.xAchse}:\n{self.mazerator.maze}")

            # Gesamtzeitdauer inkl. Berechnung des Ausgabestrings sowie Ausgabe
            totalTime: float  = time.time() - startTimeToCreate
            timeSinceCreation: float  = (totalTime * 1000) if (totalTime < 1) else totalTime
            sinceCreationTimeUnit: str  = "Millisekunden" if (totalTime < 1) else "Sekunden"

            # I n f o  A u s g a b e
            print(f" Labyrinth {self.yAchse, self.xAchse} generiert in:"
                  f"{'{:6.2f}'.format(mazeCreationTime)} {mazeCreationTimeUnit}\n"
                  f" Gesamtdauer inkl. Ausgabe in der Konsole:"
                  f"{'{:6.2f}'.format(timeSinceCreation)} {sinceCreationTimeUnit}\n")

            # E R S T E L L U N G  /  S T A R T  D E S  S P I E L S
            MazeSpiel(self.yAchse, self.xAchse, self.mazerator, player, self.screentype).run()

            # K O N S O L E N - A U S G A B E - L A B Y R I N T H  mit Lösungspfad
            self.mazerator.maze.isPrintMarker = False
            print(f" Labyrinth {self.yAchse, self.xAchse}:\n"
                  f"{self.mazerator.maze}")

        print("\nProgramm wurde beendet. Vielen Dank fürs Spielen.")

    def setXYachsen(self) -> None:                                     # Achsenwert Eingabe
        """ Nimmt die Menüauswahl des Spielers entgegen. Das Menü wird vor der Eingabe ausgegeben.

        Mögliche Fehleingaben wie z.B. statt Ziffern andere Zeichen oder zuviele wie auch zu wenige Werte, werden
        durch entsprechendes Auffangen der Exceptions verhindert.

        Durch das Betätigen der "q"-Taste kann der Benutzer das Programm komplett beenden. Der Spieler kann das
        Programm parametisiert starten. Dabei übergibt dieser je ein Wert für die y-Achse sowie ein Wert für die
        x-Achse. Wenn der Spieler die "v"-Taste betätigt, wird mit isintance geprüft, ob der Spieler tatsächlich
        Integer-Werte beim parametisierten Start des Programms eingegeben hat oder nicht. Falls Integerwerte eingegeben
        wurden, erfolgt eine weitere Prüfung durch den Aufruf der Funktion Konsole._isAchsenSizeValid, um die
        Achsenwerte zu validieren. Sind die Werte valide so wird die while-Schleife unterbrochen.

        Falls der Benutzer keine Integerwerte beim parametisierten Start des Programms übergeben hatte, wird der
        Benutzer mit deiner Fehlermeldung darauf hingewiesen. Für denn Fall, dass die übergebenen Werte beim Start des
        Programm Integerwerte waren, aber die Prüfung Konsole._isAchsenSizeValid negativ ausfällt, wird eine entsprechende
        Fehlermeldung, weshalb die angegeben Werte für y-Achse sowie x-Achse nicht valide sind ausgegeben und eine
        anschließend eine weitere Fehlermeldung, dass die übergebenen Werte nicht korrekt seien.

        Neben der Kurzschreibweise in folgender Form:  10x10 oder 10*10 kann der Benutzer durch die Eingabe der Taste
        "v" entweder beim erstmaligen Spielen ein Labyrinth der Größe 30*30 ausgeben lassen oder ab dem zweitmaligen
        Spielen die Werte, die zuvor eingegeben wurden wieder fur die Generierung eines neuen Labyrinths verwenden.

        Desweiteren kann der Benutzer zunächst durch Betätigen der Enter-Taste die Achsenwerte nacheinander eingeben.

        Die While-Schleife läuft solange bis der Spieler valide y-Achsenwert und x-Achsenwert eingegeben hat oder bis
        der Spieler die "q"-Taste betätigt.

       Quellenangabe zu dem regex, welches den userinput entweder nach "x", " " oder "*" zerteilt:
       https://stackoverflow.com/questions/4998629/split-string-with-multiple-delimiters-in-python
        """
        while True:
            try:
                userinput:str = input(konstanten.MENU).lower().strip()
                ystring, xstring = "",""     # type: str, str
                if "q" in userinput:
                    self.running = False          # type: bool
                    break
                elif "v" in userinput:
                    isAxisValid, self.yAchse, self.xAchse,self.kantenlaenge, self.screentype = \
                        getValidation_and_config(self.yAchse, self.xAchse)
                    if isAxisValid:
                        break
                elif "d" in userinput:
                    self.debug = not self.debug       # type: bool
                    print("\n", 12 * " ", "Debug Info-Ausgabe? ", self.debug)
                elif ("x" in userinput) or ("*" in userinput) or (" " in userinput):
                    xstring, ystring = re.split('[x *]',userinput)
                else:
                    xstring:str = input(" Bitte x-Achse eingeben (horizontale):")
                    ystring:str = input(" Bitte y-Achse eingeben (vertikale):")
                try:
                    self.yAchse, self.xAchse = int(ystring), int(xstring) # type: int, int
                    isAxisValid, self.yAchse, self.xAchse, self.kantenlaenge, self.screentype \
                        = getValidation_and_config(self.yAchse, self.xAchse)
                    if isAxisValid:
                        break
                except ValueError:
                    if "d" not in userinput:
                        print(konstanten.WRONG_VALUE_ERRMSG)
                except TypeError:
                    pass
            except ValueError:
                print(konstanten.TOO_MANY_VALUE_ERRMSG)


def getValidation_and_config(yAchse: int, xAchse: int) -> Union[Tuple[bool,int,int,int,int],Tuple[bool,int,int,None,None]]:  # Achsenwert Validierung
    """ Validiert Benutzereingabe, berechnet die kantenlänge einer Labyrinthwand und entscheidet über den Anzeige Modus.

    :return: Gibt Validierung, y- ,x-Achsenwert, Kantenlänge und AnzeigeModus zurück.
    :rtype:  Tuple[bool,int, int, int ,int] or Tuple[bool,int, int,None,None]
    :param yAchse: y-Achsenwert
    :type yAchse:  int
    :param xAchse:  x-Achsenwert
    :type xAchse: int
    """
    kantenlaenge, minKantenLaenge = konstanten.LAENGE, konstanten.KANTENLAENGE_MINIMUM  # type: int, int
    x_screenTotal, y_screenTotal = konstanten.SCREENSIZE  # type: int,int
    usableScreen_y = y_screenTotal - 2 * konstanten.FENSTER_RAND_ABSTAND  # type: int
    usableScreen_x = x_screenTotal - 2 * konstanten.FENSTER_RAND_ABSTAND  # type: int
    max_y_Achse = int(usableScreen_y / minKantenLaenge)  # type: int
    max_x_Achse = int(usableScreen_x / minKantenLaenge)  # type: int

    if yAchse < 10 or xAchse < 10:
        if yAchse > 0 and xAchse > 0:
            print(konstanten.AXIS_SMALLER_10_ERRMSG.replace("^", "{}").format(max_y_Achse, max_x_Achse))
        else:
            print(konstanten.AXIS_SMALLER_0_ERRMSG)
        return False,yAchse,xAchse,None,None

    elif yAchse > max_y_Achse or xAchse > max_x_Achse:
        if yAchse > xAchse:
            temp = yAchse
            yAchse = xAchse  # vertauscht yAchsenWert mit xAchsenWert
            xAchse = temp
            if yAchse > max_y_Achse or xAchse > max_x_Achse:
                print(konstanten.AXIS_TOO_BIG_ERRMSG.replace("^", "{}").format(max_y_Achse, max_x_Achse))
                return False,yAchse,xAchse,None,None
        else:
            print(konstanten.AXIS_TOO_BIG_ERRMSG.replace("^", "{}").format(max_y_Achse, max_x_Achse))
            return False,yAchse,xAchse,None,None

    kantenlaenge_y, kantenlaenge_x = int(usableScreen_y / yAchse), int(usableScreen_x / xAchse)
    kantenlaenge = min(kantenlaenge_x,kantenlaenge_y) if min(kantenlaenge_x,kantenlaenge_y) <= 30 else 30
    x_maze2ScreenRatio = xAchse * kantenlaenge / usableScreen_x
    y_maze2ScreenRatio = yAchse * kantenlaenge / usableScreen_y
    #print(f"\n\n x_maze2ScreenRatio: {x_maze2ScreenRatio},\n y_maze2ScreenRatio: {y_maze2ScreenRatio}")
    screentype = pygame.locals.FULLSCREEN if (y_maze2ScreenRatio > 0.85 or x_maze2ScreenRatio > 0.85) else pygame.locals.RESIZABLE

    print(konstanten.ISVALID_MSG)
    return True, yAchse, xAchse, kantenlaenge, screentype


def _get_args() -> argparse.Namespace:
    """ Gibt den Parser für den Zugriff auf die Argumente zurück.

    Quellenangabe:
    https://mkaz.blog/code/python-argparse-cookbook/        \n
    YOUENS-CLARK, KEN (2020): Tiny Python Projects, Seite 32. New York: Manning Publications

    :return: Gibt den Parser für den Zugriff auf die Argumente zurück.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser( description = 'Parametrisierter Start des Maze-Spiels',
                                      formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(   'axisValues', nargs = '*', type = int, help = konstanten.AXIS_HELP_MSG)
    parser.add_argument('-x', '--xaxis', nargs = 1,   type = int, help = "x-Achsenwert als Integer")
    parser.add_argument('-y', '--yaxis', nargs = 1,   type = int, help = "y-Achsenwert als Integer")
    parser.add_argument('-gui', help = konstanten.GUI_HELP_MSG, action = 'store_true')
    return parser.parse_args()

def main() -> None:
    """
    Prüft die parametrisierte Eingabe beim Start des Programms und führt entsprechende Aktion aus.

    Übergabe von nur 1 Parameter und mehr als 2 Parameter führen zur Ausgabe einer
    entsprechenden Fehlermeldung. Wenn Benutzer exakt 2 Paramter übergab, so wird das Programm
    parametrisiert gestartet und falls keine Übergaben erfolgten, dann wird das Programm ohne
    Übergabeparameter gestartet.
    Falls Benutzer Achsenwerte für x und y und [-gui] eingab, dann staret das Programm direkt in der
    graph. Ausgabe, sofern die Achsenwerte zuvor valide waren.
    """
    args = _get_args()
    if args.gui and args.xaxis and args.yaxis:  # Param.übg. wie: -x 10 -y 11 -gui
        isAxisValid, yAchse, xAchse, kantenlaenge, screentype = getValidation_and_config(args.yaxis[0], args.xaxis[0])
        if isAxisValid:
            mazerator:algo.MazeGenerator = algo.MazeGenerator(yAchse, xAchse, kantenlaenge)
            MazeSpiel(yAchse, xAchse, mazerator, model.Player(yAchse,xAchse,mazerator.spanning3), screentype).run()
    else:
        if args.xaxis and args.yaxis:            # Param.übg. wie: -x 10 -y 11 oder --xaxis 10 --yaxis 11
            print(konstanten.PARAM_MSG.format( args.xaxis[0], args.yaxis[0] ))
            Konsole(args.yaxis[0], args.xaxis[0]).run()
        elif (args.xaxis and not args.yaxis) or (not args.xaxis and args.yaxis):
            print(konstanten.ONLY_1_PARAM_ERRMSG )
        elif len(args.axisValues) == 2:                                           # Param.übg. wie: 10 10
            print(konstanten.PARAM_MSG.format( args.axisValues[0], args.axisValues[1] ))
            Konsole(args.axisValues[1], args.axisValues[0]).run()
        elif len(args.axisValues)  > 2:  print(konstanten.OVER_2_PARAM_ERRMSG)                   # Zuviele Parameter
        elif len(args.axisValues) == 1:  print(konstanten.ONLY_1_PARAM_ERRMSG)    # Unvollständige Parameterübergabe
        else:
            print(konstanten.NO_PARAM_MSG)                                                 # Keine ParameterÜbergabe
            Konsole().run()

if __name__ == '__main__':
    main()
    sys.exit()
