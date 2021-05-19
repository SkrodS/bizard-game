from enum import Enum

class Gamestate(Enum):
    MENU = 1
    RUNNING = 2
    PAUSED = 3
    GAME_OVER = 4