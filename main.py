import pygame
from save import save
from load import load
from gamestate import *
from game import *
from cryptography.fernet import Fernet
import sys

g = Game() # Skapar en instans av klassen spel. Detta är själva spelet.

while True:
    
    # Nedan följer spelets "state machine".

    # MENY
    if g.gamestate == Gamestate.MENU:
        g.new()
        g.menu_screen()

    # SPELETS GAMEPLAY
    elif g.gamestate == Gamestate.RUNNING:
        g.saved = False
        g.main()

    # NY WAVE
    elif g.gamestate == Gamestate.NEXT_WAVE:
        g.wave += 1
        for sprite in g.all_sprites:
            if sprite:
                sprite.kill()
        g.new()
        g.gamestate = Gamestate.RUNNING

    # PAUS
    elif g.gamestate == Gamestate.PAUSED:
        g.pause_screen()

    # GAME OVER
    elif g.gamestate == Gamestate.GAME_OVER:
        g.wave = 0
        g.game_over()

    # STÄNG AV
    elif g.gamestate == Gamestate.EXIT:
        sys.exit()
    
    # SVÅRIGHETSGRADS-SKÄRMEN
    elif g.gamestate == Gamestate.DIFFICULTY_SELECTION:
        g.difficulty_selection_screen()

    # NY SPELOMGÅNG (EASY)
    elif g.gamestate == Gamestate.EASY:
        g.difficulty = 2
        g.new()
        g.gamestate = Gamestate.RUNNING

    # NY SPELOMGÅNG (MEDIUM)
    elif g.gamestate == Gamestate.MEDIUM:
        g.difficulty = 4
        g.new()
        g.gamestate = Gamestate.RUNNING

    # NY SPELOMGÅNG (HARD)
    elif g.gamestate == Gamestate.HARD:
        g.difficulty = 6
        g.new()
        g.gamestate = Gamestate.RUNNING

    # SPARA EN SPELOMGÅNG
    elif g.gamestate == Gamestate.SAVE:
        save(g.wave, g.difficulty, g.player.bunny)
        g.saved = True
        g.gamestate = Gamestate.PAUSED

    # LADDA EN SPARAD SPELOMGÅNG
    elif g.gamestate == Gamestate.LOAD:
        g.wave, g.difficulty, g.bunny, g.gamestate = load()
        g.new()
