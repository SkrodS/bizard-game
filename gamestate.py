from enum import Enum

class Gamestate(Enum):
    MENU = 1
    RUNNING = 2
    NEXT_WAVE = 3
    PAUSED = 4
    GAME_OVER = 5
    EXIT = 6
    DIFFICULTY_SELECTION = 7
    EASY = 8
    MEDIUM = 9
    HARD = 10
    SAVE = 11