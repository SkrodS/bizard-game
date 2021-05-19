import pygame
from enum import Enum
from sprites import *
from config import *
from gamestate import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font = pygame.font.Font('font/rainyhearts.ttf', 16)
        self.font_big = pygame.font.Font('font/rainyhearts.ttf', 32)

        self.gamestate = Gamestate.MENU
        self.wave = 1
        self.cooldown = 0

        self.character_spritesheet = Spritesheet('img/character.png')
        self.terrain_spritesheet = Spritesheet('img/Overworld.png')
        self.enemy_spritesheet = Spritesheet('img/log.png')
        self.bullet_spritesheet = Spritesheet('img/bullets.png')
        self.object_spritesheet = Spritesheet('img/objects.png')
        self.bunny_spritesheet = Spritesheet('img/bunny.png')

    def create_tilemap(self):
        for i, row in enumerate(TILEMAP):
            for j, column in enumerate(row):
                Ground(self, j, i)
                if column == 'B':
                    Block(self, j, i)
                if column == 'P':
                    self.player = Player(self, j, i)
                    Item(self, j, i)
                if column == '-':
                    if len(self.enemies) != self.wave+2:
                        possible = [
                            'enemy',*(self.wave+2),
                            'ground',*(412-self.wave+2),
                        ]
                        print(possible)
                        choice = random.choice(possible)
                        if choice == 'enemy':
                            Enemy(self, j, i)

    def new(self):
        # ett nytt spel startar
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.players = pygame.sprite.LayeredUpdates()
        self.items = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.LayeredUpdates()
        self.menu = pygame.sprite.LayeredUpdates()

        self.create_tilemap()

    def events(self):
        #game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gamestate = Gamestate.EXIT

    def update(self):
        #game loop updates
        self.all_sprites.update()
        pygame.display.update()

    def draw(self):
        #game loop draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)

    def main(self):
        #game loop
        while self.gamestate == Gamestate.RUNNING:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        for sprite in self.all_sprites:
            sprite.kill()

        self.cooldown = pygame.time.get_ticks()
        Title(self, WIN_WIDTH/2, WIN_HEIGHT/2-40, 'Game Over', RED)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2, 'Back to Meny', WHITE, YELLOW, Gamestate.MENU)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+20, 'Quit Game', RED, YELLOW, Gamestate.EXIT)

        while self.gamestate == Gamestate.GAME_OVER:
            self.events()
            self.menu.update()
            pygame.display.update()
            self.screen.fill(BLACK)
            self.menu.draw(self.screen)
            self.clock.tick(FPS)
        
        for sprite in self.menu:
            sprite.kill()

    def pause_screen(self):
        self.cooldown = pygame.time.get_ticks()
        Title(self, WIN_WIDTH/2, WIN_HEIGHT/2-40, 'Paused', BLUE)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2, 'Continue', GREEN, YELLOW, Gamestate.RUNNING)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+15, 'Save progress', WHITE, YELLOW, print)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+30, 'Back to Menu', WHITE, YELLOW, Gamestate.MENU)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+45, 'Quit Game', RED, YELLOW, Gamestate.EXIT)

        while self.gamestate == Gamestate.PAUSED:
            self.events()
            self.menu.update()
            pygame.display.update()
            self.screen.fill(BLACK)
            self.menu.draw(self.screen)
            self.clock.tick(FPS)
        
        for sprite in self.menu:
            sprite.kill()

    def menu_screen(self):
        self.cooldown = pygame.time.get_ticks()
        Title(self, WIN_WIDTH/2, WIN_HEIGHT/2-60, 'Bizard:', PURPLE)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2-45, 'The Bunny-loving Wizard', BLUE, BLUE, Gamestate.MENU)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2, 'PLAY', GREEN, YELLOW, Gamestate.RUNNING)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+15, 'LOAD', WHITE, YELLOW, Gamestate.MENU)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+45, 'Quit Game', RED, YELLOW, Gamestate.EXIT)

        while self.gamestate == Gamestate.MENU:
            self.events()
            self.menu.update()
            pygame.display.update()
            self.screen.fill(BLACK)
            self.menu.draw(self.screen)
            self.clock.tick(FPS)
        
        for sprite in self.menu:
            sprite.kill()

g = Game()

while g.running:

    print(g.gamestate)
    if g.gamestate == Gamestate.MENU:
        g.new()
        g.menu_screen()

    elif g.gamestate == Gamestate.RUNNING:
        g.main()

    elif g.gamestate == Gamestate.PAUSED:
        g.pause_screen()

    elif g.gamestate == Gamestate.GAME_OVER:
        g.game_over()

    elif g.gamestate == Gamestate.EXIT:
        sys.exit()