import pygame
from sprites import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font = pygame.font.Font('font/rainyhearts.ttf', 16)
        self.font_big = pygame.font.Font('font/rainyhearts.ttf', 32)

        self.wave = 1

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
        self.bullets = pygame.sprite .LayeredUpdates()

        self.create_tilemap()

    def events(self):
        #game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

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
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        for sprite in self.all_sprites:
            sprite.kill()
        
        Title(self, WIN_WIDTH/2, WIN_HEIGHT/2-40, 'Game Over', RED)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2, 'Try Again', WHITE, YELLOW, self.intro_screen)
        Button(self, WIN_WIDTH/2, WIN_HEIGHT/2+20, 'Quit Game', WHITE, YELLOW, sys.exit)


        while self.running:
            self.events()
            self.update()
            self.draw()



    def intro_screen(self):
        pass

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()