import pygame, sys
from pygame.locals import *
import math
import numpy as np

FRICTION = 0.1
TOPSPEEED = 3
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


class GameObject:

    def __init__(self, pos_x, pos_y, screen, sprite):
        self.pos = pygame.Vector2(pos_x, pos_y)
        self.velocity = pygame.Vector2(1, 1)

        self.sprite = sprite
        self.screen = screen

    def update(self):
        self.pos += self.velocity

    def draw(self):
        self.screen.blit(self.sprite, self.pos)

class Player(GameObject):
    
    def __init__(self, position_x, position_y, screen, sprite):
        super().__init__(position_x, position_y, screen, sprite)

        self.stopping = True

        self.hp = 100

    def update(self, events):

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if event.key == K_w:
                    self.velocity.y = -TOPSPEEED
                    self.stopping = False
                if event.key == K_a:
                    self.velocity.x = -TOPSPEEED
                    self.stopping = False
                if event.key == K_s:
                    self.velocity.y = TOPSPEEED
                    self.stopping = False
                if event.key == K_d:
                    self.velocity.x = TOPSPEEED
                    self.stopping = False

            if event.type == KEYUP:
                self.stopping = True

        if self.stopping:
            self.velocity.x *= 1-FRICTION
            self.velocity.y *= 1-FRICTION

        super().update()



pygame.init()

#Skärmen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Player/Spelaren
player_sprite = pygame.image.load('mario.png').convert_alpha()
mario = Player(500, 0, screen, player_sprite)

# Spel-loopen
    # Har något hänt? "events"
    # Uppdatera game state
    # Rita ut på skärmen
while True:

    # Spellogik
    events = pygame.event.get()
    mario.update(events)
    
    # Rita
    # KODFRÅGA 4: Varför behövs den här raden?
    screen.fill((30, 0, 0))

    mario.draw()
    pygame.display.update()