# coding=utf-8
import ctypes      # Comment this line like this comment for use under Linux or OSX
import pygame.locals
#                                    S I Z E S
_user32 = ctypes.windll.user32  # Comment this line like this comment for use under Linux or OSX
# (x,y-Auflösung =     ┏━━━━━━━→ x-Achse           ┏━━━━━━━→  y-Achse
SCREENSIZE = _user32.GetSystemMetrics(0), _user32.GetSystemMetrics(1)   # under Linux or OSX, if FULLHD type: SCREENSIZE = (1920,1080)
SCREENTYPE = pygame.locals.RESIZABLE
LAENGE = 30
KANTENLAENGE_MINIMUM = 4
HOEHE = 1
FENSTER_RAND_ABSTAND = 2
#                                   C O L O R S
# (rot-Wert, ↓ , blau-Wert)
#    ┃    grün-Wert  ┃  Farbkodierung
#    ┗━ ━┓  ┏━┙┏━━━━━┙
BLACK = (0, 0, 0)  # (rot-Wert, grün-Wert, blau-Wert) Farbkodierung
BLAUNEON = (100, 200, 255)
GELBNEON = (255, 255, 0)
GRUENNEON = (0, 255, 0)
GRUEN_115 = (0, 115, 0)
GRUEN_180 = (0, 180, 0)
GRUEN_75 = (0, 75, 0)
PINK = (125, 0, 125)
ROT = (255, 0, 0)
ROT_25 = (255, 0, 25)
ROTDUNKEL = (100, 0, 0)
ORANGE = (200, 100, 0)
ROT_100_100= (255, 100, 100)

SOLUTIONPATHCOLOR = GRUEN_180
BGCOLOR = BLACK
WALLCOLOR_1 = ROT
WALLCOLOR_2 = ROTDUNKEL
PLAYERPATHCOLOR = GRUEN_115
VALIDMOVECOLOR = GRUENNEON
INVALIDMOVECOLOR = ROTDUNKEL
STARTCOLER = GRUENNEON
ZIELCOLER = ROT_100_100
GENERATOR_COLOR = GRUEN_75
BACKTRACKER_COLOR = GRUEN_180
#                                   M E S S A G E S
# mazespiel._get_args() Messages:
AXIS_HELP_MSG = " Die Integer-Achsenwerte x-Achse und y-Achse jeweils durch 1 Leerzeichen trennen."
GUI_HELP_MSG = "Direkter Start in die Gui für ein einmaliges Spielen, ohne Konsolenausgabe des " \
               "Labyrinths."

# mazespiel.main() Messages:
PARAM_MSG = "\n Parametrisierter Programmstart mit x-Achse = {} und y-Achse = {}."
NO_PARAM_MSG = "\n Start des Programms ohne Parameter-Übergabe."
OVER_2_PARAM_ERRMSG = "\n ERROR: Zu viele Argumente!\n Es wird je 1 x-Achse und 1 y-Achse benötigt!"
ONLY_1_PARAM_ERRMSG = OVER_2_PARAM_ERRMSG.replace("viele","wenige")

# mazespiel.Konsole.setXYachsen() Messages:
MENU = (
"""                   
                ╻    ╻    Betriebssysteme     ╻    ╻  Werkstück A7              ╻                                          
     Stella Malkogiannidou          ┃  Amaal Mohamed    ┃    ┃           Samira Hersi      
      ┏━━━━┓    ┃    ┃    ━━━━━━━━━━┻━━━━┓    ┃    ┃    ┗━━━━╋━━━━    ┃    ┏━━━━┛    
      ┃    ┃    ┃    ┃    ╔══════════════╩════╩════╩═════════╩═══╗    ┃    ┃         
     ━┛    ┃    ┗━━━━┛    ║   M a z e G a m e  M E N Ü   ┌╍╍╍╍╍╍╍╫━━━━┫    ╹    ┏━━━━     
           ┃              ╠══════════════════════════════╡Eingabe╣    ┃         ┃          
     ━┓    ┣━━━━━━━━━━━━━━╢ Parametrisierter Start oder  ┣╍╍╍╍╍╍╍╢    ┃    ┏━━━━┛         
      ┃    ┃              ║ xy-Achse der vorigen Runde?  │ [ v ] ║    ┃    ┃                                                     
      ┃    ╹    ┏━━━━┓    ╠╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┿╌╌╌╌╌╌╌╢    ╹    ╹    ╻                                                
      ┃         ┃    ┃    ║ xy-Achse zusammen eingeben? ╭│ 35x35 ║              ┃                                                
     ━┻━━━━━━━━━┛    ┣━━━━╢ TRENNER:'x',' ','*' wie Bsp→╯│[Enter]╠━━━━━━━━━━━━━━╋━━━━                                            
                     ┃    ╠╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┿╌╌╌╌╌╌╌╢              ┃                                                
     ━┓    ╺━━━━┳━━━━┛    ║ Einzeleingabe  der xy-Achse? │[Enter]║    ╺━━━━┓    ┃                                           
      ┃         ┃         ╠══════════════════════════════╪═══════╣         ┃    ┃                                              
      ┗━━━━┓    ┃    ╺━━━━╢ Programm  beenden  mit Taste │ [ q ] ╠━━━━╸    ┃    ┃                                                
           ┃    ┃         ╠══════════════════════════════╪═══════╣         ┃    ┃                                                
     ━╸    ┃    ┗━━━━┓    ║ Labyrinth als Daten ausgeben ┕━[ d ]━╢    ┏━━━━┛    ┃                                                
           ┃         ┃    ║ Info: y = Vertikale, x = Horizontale ║    ┃         ┃                                                
     ━━━━━━┫    ╺━━━━┛    ╚════╦══════════════╦════╦════════╦════╝    ┗━━━━┓    ┃                                                
           ┃           Frankfurt University of Applied Sciences 2021       ┃    ┃
     >?> """)

WRONG_VALUE_ERRMSG = (
    "\n ERROR: Falls Option 'Eingabe zusammen' gewählt wurde, dann bitte nur:\n"
    "                                       [y-Achse][x][x-Achse] eingeben\n"
    " OHNE Leerzeichen & als Trenner nur ein kleines 'x' wie z.B.:\n"
    "                                               50x50\n"
    " Bei EinzelEingabe und für die Achsen bitte NUR GANZE POSITIVE ZAHLEN "
    "eingeben!"
    "\n")

TOO_MANY_VALUE_ERRMSG = "\n\t ERROR! Es wurden mehr als 2 Werte eingegeben!\n"

# mazespiel.getValidation_and_config() Messages:
AXIS_TOO_BIG_ERRMSG = (f"\n\t ERROR! Bei Ihrer Auflösung von {SCREENSIZE[0]}px, "
    f"{SCREENSIZE[1]}px können Sie maximal für\n\t y-Achse: ^ und für x-Achse: ^"
    f" eingeben, sodass das generierte\n\t Labyrinth vollständig dargestellt werden"
    f" kann!\n")

AXIS_SMALLER_10_ERRMSG \
    = (f"\n\t ERROR! Die Achsenwerte sollten mindestens 10 betragen,"
       f"\n\t da die Wahrscheinlichkeit steigt, dass zufällig das"
       f"\n\t Start- und Zielfeld an der selben Koordinate y,x liegen!"
       f"\n\n\t Info:{AXIS_TOO_BIG_ERRMSG[9:]}\n")

AXIS_SMALLER_0_ERRMSG="\n\t ERROR! Achsenwerte dürfen nicht kleiner gleich 0 sein!\n"

ISVALID_MSG = ("\n\n Validierung der Achsenwerte erfolgreich beendet!\n\n"                                       
              " In kürze ercheint ein Labyrinth in der Konsole und direkt im\n"
              " Anschluss die graphische Ausgabe, die entweder als Fenster oder\n"
              " Vollbild erfolgt.\n Viel Spaß beim Spielen...\n\n\n")

# mazespiel.MazeSpiel.do_printGameMetrics() Messages:
AUSWERTUNG_MSG = " Auswertung:\n Das Spiel wurde nach {} Sekunden  {}  beendet.\n" \
                 " Es wurde {} Mal das Start- und Ziel-Feld neu vergeben.\n"

SOLUTION_MSG = " Spieler Gesamtschrittanzahl: {}\n " \
               "\t- valide Schrittanzahl:   {} ({} %)\n" \
               "\t- invalide Schrittanzahl: {} ({} %)\n"\
               " Lösungspfadlänge: {}\n" \
               " Spieler-Effizienz: {} %\n\n"
