import pygame
from sprites import *
from config import *
from gamestate import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font = pygame.font.Font('font/rainyhearts.ttf', 16)
        self.font_big = pygame.font.Font('font/rainyhearts.ttf', 32)

        self.bunny = 0

        self.gamestate = Gamestate.MENU
        self.wave = 1
        self.saved = False
        self.difficulty = 0
        self.cooldown = 0

        self.character_spritesheet = Spritesheet('img/character.png')
        self.terrain_spritesheet = Spritesheet('img/Overworld.png')
        self.enemy_spritesheet = Spritesheet('img/log.png')
        self.bullet_spritesheet = Spritesheet('img/bullets.png')
        self.object_spritesheet = Spritesheet('img/objects.png')
        self.bunny_spritesheet = Spritesheet('img/bunny.png')

    def create_tilemap(self):
        enemies = 0
        tilemap = [
            'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
            'B......................................B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.-------...BB------------------------.B',
            'B.------B.....---------BBBB---B-------.B',
            'B.------B.P...----------------BB------.B',
            'B.-----BB.....------------------------.B',
            'B.-------.....--BBBBBB----------------.B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.-------BBB-----------------BBBB-----.B',
            'B.------------------------------------.B',
            'B.-----------------BBB-------------B--.B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.------B---------------------BB------.B',
            'B.-----BB-----------------------------.B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.------------------------------------.B',
            'B.-------BBB-----------------BBBB-----.B',
            'B.------------------------------------.B',
            'B.------------BBB------------------B--.B',
            'B.------------------------------------.B',
            'B......................................B',
            'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
        ]

        while True:
            target_row = random.randint(0,len(tilemap)-1)
            target_column = random.randint(0,len(tilemap[target_row])-1)
            if tilemap[target_row][target_column] == '-':
                tilemap[target_row] = tilemap[target_row][:target_column] + 'E' + tilemap[target_row][target_column+1:]
                enemies += 1
            if enemies == self.wave+2:
                break

        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i)
                if column == 'B':
                    Block(self, j, i)
                if column == 'P':
                    self.player = Player(self, j, i, self.bunny)
                    Item(self, j, i)
                if column == 'E':
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
        Title(self, WIN_WIDTH/2, WIN_HEIGHT/2-30, 'Paused', BLUE)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+10, 'Continue', GREEN, YELLOW, Gamestate.RUNNING)

        if not self.saved:
            Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+25, 'Save progress', WHITE, YELLOW, Gamestate.SAVE)
        elif self.saved:
            Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+25, 'Save progress', GRAY, GRAY, Gamestate.PAUSED)

        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+40, 'Back to Menu', WHITE, YELLOW, Gamestate.MENU)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+55, 'Quit Game', RED, YELLOW, Gamestate.EXIT)
        if self.difficulty == 2:

            Button(self, WIN_WIDTH/2, 10, f'Difficulty: EASY', GREEN, GREEN, Gamestate.PAUSED)
        if self.difficulty == 4:
            Button(self, WIN_WIDTH/2, 10, f'Difficulty: MEDIUM', ORANGE, ORANGE, Gamestate.PAUSED)
        if self.difficulty == 6:
            Button(self, WIN_WIDTH/2, 10, f'Difficulty: HARD', RED, RED, Gamestate.PAUSED)
            
        Button(self, WIN_WIDTH/2, 25, f'Wave: {self.wave}', PURPLE, PURPLE, Gamestate.PAUSED)
            

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
        self.wave = 1
        self.bunny = 0
        Title(self, WIN_WIDTH/2, WIN_HEIGHT/2-60, 'Bizard:', PURPLE)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2-45, 'The Bunny-loving Wizard', BLUE, BLUE, Gamestate.MENU)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2, 'PLAY', GREEN, YELLOW, Gamestate.DIFFICULTY_SELECTION)
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

    def difficulty_selection_screen(self):
        self.cooldown = pygame.time.get_ticks()
        Button(self, WIN_WIDTH/2-60, WIN_HEIGHT/2, 'EASY', GREEN, YELLOW, Gamestate.EASY)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2, 'MEDIUM', ORANGE, YELLOW, Gamestate.MEDIUM)
        Button(self, WIN_WIDTH/2+60, WIN_HEIGHT/2, 'HARD', RED, YELLOW, Gamestate.HARD)

        while self.gamestate == Gamestate.DIFFICULTY_SELECTION:
            self.events()
            self.menu.update()
            pygame.display.update()
            self.screen.fill(BLACK)
            self.menu.draw(self.screen)
            self.clock.tick(FPS)
        
        for sprite in self.menu:
            sprite.kill()