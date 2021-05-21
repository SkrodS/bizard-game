import pygame
from save import save
from load import load
from gamestate import *
from game import *
from cryptography.fernet import Fernet
import sys

g = Game()

while g.running:
    
    if g.gamestate == Gamestate.MENU:
        g.new()
        g.menu_screen()

    elif g.gamestate == Gamestate.RUNNING:
        g.saved = False
        g.main()

    elif g.gamestate == Gamestate.NEXT_WAVE:
        g.wave += 1
        for sprite in g.all_sprites:
            if sprite:
                sprite.kill()
        g.new()
        g.gamestate = Gamestate.RUNNING

    elif g.gamestate == Gamestate.PAUSED:
        g.pause_screen()

    elif g.gamestate == Gamestate.GAME_OVER:
        g.wave = 0
        g.game_over()

    elif g.gamestate == Gamestate.EXIT:
        sys.exit()
    
    elif g.gamestate == Gamestate.DIFFICULTY_SELECTION:
        g.difficulty_selection_screen()

    elif g.gamestate == Gamestate.EASY:
        g.difficulty = 2
        g.new()
        g.gamestate = Gamestate.RUNNING

    elif g.gamestate == Gamestate.MEDIUM:
        g.difficulty = 4
        g.new()
        g.gamestate = Gamestate.RUNNING

    elif g.gamestate == Gamestate.HARD:
        g.difficulty = 6
        g.new()
        g.gamestate = Gamestate.RUNNING

    elif g.gamestate == Gamestate.SAVE:
        save(g.wave, g.difficulty)
        g.saved = True
        g.gamestate = Gamestate.PAUSED

    elif g.gamestate == Gamestate.LOAD:
        g.wave, g.difficulty, g.gamestate = load()
        g.new()
