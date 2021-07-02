# coding=utf-8
import pygame
import random
import typing
import konstanten
from konstanten import *

class Koordinate(object):
    """Die Eigenschaften (Attribute) beinhalten u.a. horizontale und/oder vertikale Kante, Start- oder Ziel-Feld,...

    ...Feld für Spieler-Position, Spieler-Wegverlauf, Lösungspfad-Feld, Spannbaum-Feld und zu jedem dessen Farbe.
    Desweiteren noch zur Generierung die Nachbarn der Koordinaten-Instanz und ob diese besucht wurde oder nicht. """

    def __init__(self, y: int, x: int, kantenlaenge: int) -> None:
        self.y: int = y  # Vertikale   - Achse
        """ Gibt zusammen mit self.x die Stelle im 2D-Array labyrinth an, wo sich diese Koordinaten-Instanz befindet."""

        self.x: int = x  # Horizontale - Achse
        """ Gibt zusammen mit self.y die Stelle im 2D-Array labyrinth an, wo sich diese Koordinaten-Instanz befindet."""
        
        self.laenge: int = kantenlaenge
        """ Gibt die Länge einer Feld-Kante für die graph. Ausgabe an. Wird zum Berechnen des pygame.Rect-Objekts in 
        Koordinate.rect benötigt. """

        self.kanten: dict = {}
        """ Beinhaltet 0-2 Kanten des Typs pygame.Rect-Objekts. Jede Koordinaten-Instanz hat nach Aufruf der Methode 
        MazeGenerator.createWalls() 2 Kanten, die über den Schlüssel "h" und "Schlüssel "v" gelöscht werden im Falle der
         Labyrinth-Generierung. Zum späteren Anzeigen in der graph. Ausgabe, wird via Schlüssel "h" und/oder "v" auf das 
         pygame.Rect-Objekt zugegriffen, um diesen auf die Anzeige zeichnen zu können und nach dem Zeichnen des Laberyinths
         anzuzeigen. """

        self.marker = ""                         # type: pygame.Rect or str
        """ Das Attribut beinhaltet ein pygame.Rect-Objekt, wodurch ein Feld des Labyrinths in der graph. Ausgabe gezeichnet 
        wird. Die Erstellung des Objekts pygame.Rect erfolgt entweder durch den Aufruf der Methode Koordinate.rect. 
        Das Feld dient für die Anzeige eines Start-, Ziel-, Spieler-Wegverlauf-, Spieler-Position- oder  
            stehen. Die Unterscheidung zwischen den verschiedenen Feldern erfolgt durch die Farbe in markerColor, die
            durch jeweils einer anderen Farbe gekennzeichnet ist.
        """

        self.markerColor = None                  # type: None or typing.Tuple[int, int, int]
        """ Beinhaltet eine RGB-Farbe des marker-Felds aus den konstanten-Modul wie zum Beispiel: 
        konstanten.STARTCOLER...."""

        self.solutionMarker = None
        """ Das Attribut beinhaltet ein pygame.Rect-Objekt, wodurch ein Feld des Labyrinths in der graph. Ausgabe gezeichnet 
        wird. Die Erstellung des Objekts pygame.Rect erfolgt entweder durch den Aufruf der Methode 
        algo.PathFinder.calculate oder durch Koordinate.rect Methode. Das Feld dient für die Anzeige eines Lösungsweges 
        oder Spannbaums. """

        self.solutionMarkerColor = None          # type: None or typing.Tuple[int, int, int]
        """Beinhaltet eine RGB-Farbe des marker-Felds aus den konstanten-Modul wie zum Beispiel: 
        konstanten.SOLUTIONPATHCOLOR, konstanten.GENERATOR_COLOR, konstanten.BACKTRACKER_COLOR."""
        
        #                    right            down         left             up
        self.neighbours = [(y, x+1, "v"), (y+1, x, "h"), (y, x-1, "v"), (y-1, x, "h")] # type: typing.List[typing.Tuple[int, int, str]]
        """Gibt die Nachbarn dieser Koordinate-Instanz an. Wird beim Generieren des Labyrinths benötigt. """
        
        self.isVisited: bool = False
        """Gibt an, ob diese Koordinate-Instanz bereits besucht wurde oder nicht. Wird beim Generieren des Labyrinths 
        benötigt."""

    def __repr__(self) -> str:
        """
        Gibt einen repräsentativen String dieser Klasse Koordinate für die Ausgabe in der Konsole zurück.

        Ohne diese Angabe wird sonst in der Konsole nur die Speicheradresse dieser Objektinstanz der Klasse Koordinate
        ausgegeben.

        :return: Ein String für die Konsolenausgabe
        :rtype: str
        """
        return "{},{}".format(self.y, self.x)

    @property
    def getKoordinatenKantenDaten(self) -> str:
        """ Gibt den repräsentativen String dieser Objektinstanz sowie Repräsentation der Daten des Dictionarys kanten

        als Schlüssel-Wert-Paar (key, value) zurück.

        :return: Einen formatierten String, welches diese Klasse repräsentiert (self) und die interne Struktur des
        kanten-Dictionary, durch Schlüssel-Wert-Paar zurück gibt.
        :rtype: str
        """
        return f" |[{self}]←{self.kanten}|"

    @property
    def rect(self) -> pygame.Rect:
        """ Berechnung eines rechteckigen Feldes, der diese Koordinate in der graf. Labyrinthausgabe repräsentiert.

        Berechnung wird im marker dieser Koordinate abgespeichert. die durch unterschiedliche Einfärbung via markerColor
        imstande ist eine Unterscheidung zwischen dem Start- und Zielfeld, sowie Player-Wegverlauf anzuzeigen.

        Die Berechnung basiert quasi wie die Berechnung der kante, nur muss man die Kanten rausrechnen,
        dh. Der Punkt x,y + Breite und die Länge (width) sowie die Breite (height) sind beides gleich LAENGE,
        die global definiert wurde

        :return:
        :rtype: pygame.Rect
        :return:
        :rtype:
        """
        x:     int = konstanten.FENSTER_RAND_ABSTAND + self.x * self.laenge
        y:     int = konstanten.FENSTER_RAND_ABSTAND + self.y * self.laenge
        width: int = self.laenge
        height:int = self.laenge
        return pygame.Rect(x, y, width, height)


class Maze(object):
    def __init__(self, yAchse: int, xAchse: int, kantenlaenge:int) -> None:
        """  Bildet den Urzustand des 2D-Arrays labyrinth,

        indem für jede Stelle des labyrinth-2D-Arrays eine neue Objektinstanz der Klasse Koordinate
        gespeichert wird. Jeder Instanz wird dessen Position im 2D-Array übergeben und zusätzlich die
        kantenlänge einer Wand im Labyrinth. Das 2D-Array ist um eine Zeile (y) und Spalte (x) länger
        wie vom Benutzer eingegeben.

        wallStartChar beinhaltet eine Pseudo Binärkodierung zu dem Kanten-Startzeichen einer
        horizontalen Kante im Labyrinth an der Stelle y,x. Um die Kante als Wert zu erhalten,
        wird der Schlüssel in der Mehtode berechnet und durch in wallStartChar angegeben.

        :param yAchse:
        :type yAchse: int
        :param xAchse:
        :type xAchse: int
        :param kantenlaenge:
        :type kantenlaenge: int
        """
        self.yAchse, self.xAchse = yAchse, xAchse     # type: int, int
        self.isPrintMarker: bool = True
        """ Dient als Switch zwischen der Ausgabe des Koordinate.marker- oder Koordinate.solutionMarker-Feldes bei der 
        Ausgabe des Labyrinths in der Konsole."""

        self.labyrinth:     typing.List[typing.List[Koordinate]] = [[Koordinate(row, colmn, kantenlaenge)
                                                                     for colmn in range(self.xAchse + 1)]
                                                                    for row in range(self.yAchse + 1)]
        """ Ist ein 2D-Array des Datentyps Koordinate. Jede Stelle im labyrinth beinhaltet eine Koordinaten-Instanz, um 
         bei der Ausgabe des labyrinths dessen Eigenschaften ausgeben zu können."""

        self.wallStartChar: typing.Dict[str, str] = {'1111': '╋', '0111': '┫', '1011': '┻', '1101': '┣', '1110': '┳',
                                                     '0011': '┛', '1001': '┗', '1100': '┏', '0110': '┓', '0101': '┃',
                                                     '1010': '━', '0001': '╹', '1000': '╺', '0100': '╻', '0010': '╸',
                                                     '0000': ' '}
        """Beinhaltet die Kanten-Startzeichen. Durch die Angabe des Binärcode-Schlüssels zurück, gibt dieses Dictionary
        das entsprechende Kanten-Startzeichen zurück. Der Schlüssel wird durch den Methoden-Aufruf _getZeichenCode 
        berechnet."""

    def isValid_and_isNotVisited(self, y: int, x: int) -> bool:
        """ Prüft ob die Koordinate y,x innerhalb des Laberyinths liegt und das Feld unbesucht ist.

        :param y: Der y-Wert, der zu überprüfen gilt.
        :type y:  int
        :param x: Der x-Wert, der zu überprüfen gilt.
        :type x:  int
        :return: True, falls Koordinate y,x innerhalb des Labyrinth und falls diese Feld
        (Koordinateninstanz) unbesucht ist, sonst False.
        :rtype:  bool
        """
        return (0 <= y < self.yAchse) and (0 <= x < self.xAchse) \
               and not self.labyrinth[y][x].isVisited

    def isValid(self, y: int, x: int) -> bool:
        """ Prüft ob die Koordinate y,x innerhalb des Laberyinths liegt.

        Wird durch die Methode _getZeichenCode(self,ky, kx) aufgerufen.

        :param y: Der y-Wert, der zu überprüfen gilt.
        :type y:  int
        :param x: Der x-Wert, der zu überprüfen gilt.
        :type x:  int
        :return: True, falls Koordinate y,x innerhalb des Labyrinth, sonst False.
        :rtype:  bool
        """
        return 0 <= y < self.yAchse and 0 <= x < self.xAchse

    def __repr__(self) -> str:
        """ Bildet den String für die Konsolenausgabe des Labyrinths in UniCode.

        Jede Zeile muss zweimal hintereinander berechnet werden, um in einer Zeile sofern vorhanden, nur
        die horizontale Kante mit der berechneten kantenstartZeichen dem ausabe-String hinzugefügt.
        Jede Spalte (x) hat die Länge von 5 UniCode Zeichen.  In der andern Zeile werden sofern es
        eine Kante gibt die vertikale Kante mit einem Unicode Zeichen dem ausabe-String hinzugefügt.

        :return: Der superlange String für die Konsolenausgaeb des Labyrinths
        :rtype: str
        """
        ausgabe = " "
        for y in range(self.yAchse + 1):
            for x in range(self.xAchse):       # Zeile: H-Kante-Zeile
                if "h" in self.labyrinth[y][x].kanten:
                    ausgabe += '{}━━━━'.format(self.wallStartChar[self._getZeichenCode(y, x)])
                else:
                    ausgabe += '{}    '.format(self.wallStartChar[self._getZeichenCode(y, x)])
            ausgabe += '{}\n '.format(self.wallStartChar[self._getZeichenCode(y, self.xAchse)])

            for x in range(self.xAchse + 1):  # Zeile: V-Kante-Zeile
                if "v" in self.labyrinth[y][x].kanten:
                    if self.labyrinth[y][x].marker and self.isPrintMarker:
                        ausgabe += '┃{}'.format(self.labyrinth[y][x].marker)
                    elif self.labyrinth[y][x].solutionMarker and not self.isPrintMarker:
                        ausgabe += '┃ ██ '
                    else:
                        ausgabe += '┃    '
                else:
                    if self.labyrinth[y][x].marker and self.isPrintMarker:
                        ausgabe += ' {}'.format(self.labyrinth[y][x].marker)
                    elif self.labyrinth[y][x].solutionMarker and not self.isPrintMarker:
                        ausgabe += '  ██ '
                    else:
                        ausgabe += '     '
            ausgabe += '\n '

        ausgabe = ausgabe[:(-5 * self.xAchse) - 10] + '┛\n'
        return ausgabe

    def _getZeichenCode(self, ky, kx) -> str:
        """ Bildet die 4-Stellige Kantenstartzeichen-Binärkodierung und gibt diese zurück.

                              ┌─────────┬─────────────┬─────────┐
        ┌───────────────┬─────┤Anzahl: 3│  Anzahl: 2  │Anzahl: 1│
        │ Prüfungs-     │     │Existiert│eine Kante um│ K herum?│
        │ reihenfolge   │ ╋   │ ┫ ┻ ┣ ┳ │ ┛ ┗ ┏ ┓ ┃ ━ │ ╹ ╺ ╻ ╸ │
        ├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┼┄┤
        │ nachRechts: ━ ┼ 1 0 │ 0 1 1 1 │ 0 1 1 0 0 1 │ 0 1 0 0 │
        │ nachUnten : ┃ ┼ 1 0 │ 1 0 1 1 │ 0 0 1 1 1 0 │ 0 0 1 0 │
        │ vonLinks *: ━ ┼ 1 0 │ 1 1 0 1 │ 1 0 0 1 0 1 │ 0 0 0 1 │
        │ vonOben * : ┃ ┼ 1 0 │ 1 1 1 0 │ 1 1 0 0 1 0 │ 1 0 0 0 │
        └───────────────┴━┼─┼─┴─────────┴─────────────┴─────────┘
        * die Prüfung     │ ┗ Dieser Fall sollte niemals vorkommen
        dieser Kanten     │   aber kommt vor und zwar NUR an den
                          │   RANDERN rechts und unten!
        erfolgt nicht     ┗━━  Es gibt doch Fälle, worin eine
        in der gleichen      dieses vorkommt.
        K-Instanz wie nachRechts o. nachUnten,  sondern in einer anderen Koordinate.

        KoordinatenInstanz = K-Instanz
        Berechnet nach den folgenden Prüfungsregeln:
        Eine +"1", wenn akt. K-Instanz eine horizontale Kante (Schlüssel "h") hat, sonst +"0"
        Eine +"1", wenn akt. K-Instanz eine vertikale Kante (Schlüssel "v") hat, sonst +"0"
        Eine +"1", wenn linke vom akt. K-Instanz eine Horizontale Kante (Schlüssel "h") hat, sonst +"0"
        Eine +"1", wenn obere vom akt. K-Instanz eine vertikale Kante (Schlüssel "v") hat, sonst +"0"

        Anschließend erfolgt eine Korrektur für KantenStartZeichen des rechten und unteren
        Rands, die den ZeichenCode komplett ersetzt durch das korregierte.
        Siehe dazu die Kommentare im Quellcode, was wie wann und warum ersetzt wird.

        :param ky:
        :type ky: int
        :param kx:
        :type kx: int
        :return: Die "Binärkodierung" für den Kantenstartzeichen.
        :rtype: str
        """
        zeichenCode =  "1" if 'h' in self.labyrinth[ky][kx].kanten \
                  else "0"
        zeichenCode += "1" if 'v' in self.labyrinth[ky][kx].kanten \
                  else "0"
        zeichenCode += "1" if (self.isValid(ky, kx - 1) and 'h' in self.labyrinth[ky][kx - 1].kanten) \
                  else "0"
        zeichenCode += "1" if (self.isValid(ky - 1, kx) and 'v' in self.labyrinth[ky - 1][kx].kanten) \
                  else "0"
        #           ┏→ Rand unten     ┏→ 1.EckeUntenLinks   ┏→  2.Sonderfall          ┏→ 3.S.fall
        if (ky == self.yAchse and not kx == 0) and (zeichenCode == '1000' or zeichenCode == '1001'):
           #        ┏→'━' if ↓    GLEICH ↓   ┏→'╺' ┏ELSE  ┏→'┻'     ┗→'━'                    ┗→'┗',
            return '1010' if zeichenCode == '1000' else '1011'
        #      ┏→ Rand rechts               ┏→ 4.EckeObenRechts      ┏→ 5.Sonderfall         ┏→ 6.S.fall
        if (kx == self.xAchse and not ky == 0) and (zeichenCode == '0100' or zeichenCode == '0110'):
                 #  ┏→'┃' if     ↓ GLEICH ↓  ┏→'╻'  ┏ELSE  ┏→'┫'      ┗→'╻'                  ┗→'┓'
            return '0101' if zeichenCode == '0100' else '0111'

        return zeichenCode


class Player(object):
    def __init__(self, y_achse:int, x_achse:int, spanningTree: dict) -> None:
        """ Beim Instanziieren werden Start und Ziel-Feld zufällig gewählt.

        Vergibt zufällige Start und Ziel-Feld Kooordinaten. Falls diese sich überlappen, werden diese
        neu vergeben. Dies geschieht solange bis Start und Ziel-Feld verschieden sind. Die Chance, dass
        diese sich überhaupt überlappen wird immer geringer je größer das Feld ist. Durch die
        while-Schleife kann jedoch garantiert werden, dass bei einer Überlappung ein weiteres mal
        zufällig vergeben wird.

        :param y_achse: y-Achsenwert
        :type y_achse: int
        :param x_achse: x-Achsenwert
        :type x_achse: int
        :param spanningTree: Der Spannbaum aus MazeGenerator.spanningTree
        :type spanningTree: Dict
        """
        self.currentKy, self.zielKy, self.currentKx, self.zielKx = 0, 0, 0, 0
        """ Die aktuelle Spielerposition oder Zielfeldposition."""

        while (self.currentKy, self.currentKx) == (self.zielKy, self.zielKx):
            self.currentKy, self.zielKy = random.randint(0, y_achse - 1), random.randint(0, y_achse - 1)
            self.currentKx, self.zielKx = random.randint(0, x_achse - 1), random.randint(0, x_achse - 1)
            
        self.spanningTree = spanningTree
        """Der Spannbaum, der zur Überprüfung der Spielerbewegung gebraucht wird."""

    def isDirectionValid(self, yvon:int, xvon:int, ynach:int, xnach:int) -> bool:
        """Prüft im spanningTree, ob in der Werteliste des Schlüssels (yvon, xvon) ← der Wert (ynach,xnach) vorkommt.

    Zur Überprüfung, ob die Richtung erlaubt ist, wird lediglich die aktuelle Position als Koordinate y,x für den
    Schlüssel benötigt und in dessen Werte-Liste nach dem (ynnach, xnach)-Wert gesucht. Die Überprüfung,
    ob eine Wand zwischen der aktuellen Position und dem nächsten Koordinatenfeld ist oder das nächste Koordinatenfeld
    überhaupt im Labyrinth liegt, findet nicht statt, da das spanning3 nur Pfade, die durch Von-Schlüssel und einer
    Liste von Nach-Werten, beinhaltet. Die Funktion isDirectionValid gibt ein True zurück, wenn die Bewegung des
    Spielers valide ist, weil die Nach-Koordinate y,x sich in der Liste der Von-Koordinaten-Schlüssel befindet,
    ansonsten gibt die Funktion ein False zurück.

        :param yvon: Die y Koordinate der aktuellen Position des Spielers als Integer.
        :type yvon: int
        :param xvon: Die x Koordinate der aktuellen Position des Spielers als Integer.
        :type xvon: int
        :param ynach: Die y Koordinate des nächsten Feldes wohin sich der Spieler hinzubewegen gedenkt als Integer.
        :type ynach: int
        :param xnach: Die x Koordinate des nächsten Feldes wohin sich der Spieler hinzubewegen gedenkt als Integer.
        :type xnach: int
        :return: Gibt ein True zurück, wenn die ynach, xnach Koordinate in der Liste als Wert des Koordinatenschlüssels
        yvon, xvon existiert, sonst False.
        :rtype: bool
        """
        return [ynach, xnach] in self.spanningTree[(yvon, xvon)]

    def setPos(self, ky: int, kx: int) -> None:
        """ Setzt die neue Position des Spielers, wo sich dieser im Labyrinth befindet.

        :param ky: Der Zeilen-Index des äußeren Arrays des 2D-Arrayliste labyrinth der Klasse Maze
        :type ky: int
        :param kx: Der Spalten-Index des inneren Arrays des 2D-Arrayliste labyrinth der Klasse Maze
        :type kx: int
        """
        self.currentKy, self.currentKx = ky, kx

    def getPos(self) -> typing.Tuple[int, int]:
        """ Gibt die aktuelle Spieler-Position, wo sich der Spieler im Labyrinth befindet, zurück.

        :return: Gibt die aktuelle y,x Koordinate (Zeilen- und Spalten-Index) zurück.
        :rtype: Tuple[int, int]
        """
        return self.currentKy, self.currentKx


class Stack(object):
    def __init__(self) -> None:
        """ Initialisiert eine leere Arrayliste als Datenspeicher """
        self.liste = []  # type: list
        """ Der Datenspeicher des Stacks."""

    def push(self, koordinate: Koordinate) -> None:
        """ Erweitert die Stack.liste um die übergebene Koordinate,

        sodass diese als erstes nach dem LiFo-Prinzip durch Stack.popp() zurück gegeben werden kann.

        :param koordinate: Die Koordinate, die ganz oben (Top) auf dem Stack steht.
        :type koordinate: model.Koordinate
        """
        self.liste.append(koordinate)

    def popp(self) -> Koordinate:
        """ Gibt die Koordinate, die zuletzt durch die Funktion Stack.push(Koordinate) hinzugefügt wurde, zurück.

        Nach dem Last-in-First-out-Prinzip (LiFo) wird die Koordinate, die zuletzt durch die Funktion
        Stack.push(Koordinate) ins Stack gepusht wurde (auf dem Stapel gelegt), aus der self.liste entfernt und
        anschließend dort wo diese Funktion aufgerufen wurde, zurück gegeben.
        #todo
        :return: Die Koordinate, die zuletzt auf dem Stack gepusht wurde
        :rtype: model.Koordinate
        """
        return self.liste.pop(-1)

    @property
    def size(self) -> int:
        """  Gibt die Größe der Stack.liste zurück

        :return: Die Elementanzahl der Stack.liste als Integer.
        :rtype: int
        """
        return len(self.liste)

    def isNotEmpty(self) -> bool:
        """ Gibt ein Boolean True zurück, wenn der Stack.liste nicht leer ist, sonst False.

        :return: Gibt den Status des Stacks als Boolean zurück.
        :rtype: bool
        """
        return self.size != 0

    def __repr__(self) -> str:
        """ Gibt die Koordinate-Instanzen des Lösungspfads als repräsentativen String für die Konsolenausgabe zurück.

        Wurde zu Debugzwecke gebraucht.

        :return: Ein repräsentativer String der Daten in der Stack.liste
        :rtype: str
        """
        ausgabe = ""
        for koordinate in self.liste: ausgabe += f"({koordinate}), "
        return ausgabe