import pygame
from config import *
import math
import random

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite

class Sprites(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.x_change = 0
        self.y_change = 0

class Player(Sprites):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.players
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT

        self.facing = 'down'
        self.animation_loop = 1

        self.health = 3
        self.collision_immune = False
        self.collision_time = 0

        self.image = self.game.character_spritesheet.get_sprite(1, 6, self.width-3, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.movement()
        self.animate()
        self.collide_enemy()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_s]:
            for sprite in self.game.all_sprites:
                sprite.rect.y -= PLAYER_SPEED
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

        if keys[pygame.K_w]:
            for sprite in self.game.all_sprites:
                sprite.rect.y += PLAYER_SPEED
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'

        if keys[pygame.K_a]:
            for sprite in self.game.all_sprites:
                sprite.rect.x += PLAYER_SPEED
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'

        if keys[pygame.K_d]:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= PLAYER_SPEED
            self.x_change += PLAYER_SPEED
            self.facing = 'right'

    def collide_enemy(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if pygame.time.get_ticks() - self.collision_time > 1000:
            self.collision_immune = False
        if hits and not self.collision_immune:
            self.health -= 1
            self.collision_immune = True
            self.collision_time = pygame.time.get_ticks()
            print(f'HP: {self.health}')
        if self.health <= 0:
            self.kill()
            self.game.playing = False

    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if direction == 'x':
            if hits:
                if self.x_change > 0:
                    for sprites in self.game.all_sprites:
                        sprites.rect.x += PLAYER_SPEED
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    for sprites in self.game.all_sprites:
                        sprites.rect.x -= PLAYER_SPEED
                    self.rect.x = hits[0].rect.right

        if direction == 'y':
            if hits:
                if self.y_change > 0:
                    for sprites in self.game.all_sprites:
                        sprites.rect.y += PLAYER_SPEED
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    for sprites in self.game.all_sprites:
                        sprites.rect.y -= PLAYER_SPEED
                    self.rect.y = hits[0].rect.bottom

    def animate(self):
        down_animations = [
            self.game.character_spritesheet.get_sprite(1, 6, self.width, self.height),
            self.game.character_spritesheet.get_sprite(17, 7, self.width, self.height),
            self.game.character_spritesheet.get_sprite(33, 6, self.width, self.height),
            self.game.character_spritesheet.get_sprite(49, 7, self.width, self.height),
        ]

        up_animations = [
            self.game.character_spritesheet.get_sprite(0, 69, self.width, self.height),
            self.game.character_spritesheet.get_sprite(16, 70, self.width, self.height),
            self.game.character_spritesheet.get_sprite(32, 69, self.width, self.height),
            self.game.character_spritesheet.get_sprite(48, 70, self.width, self.height),
        ]

        left_animations = [
            self.game.character_spritesheet.get_sprite(1, 102, self.width, self.height),
            self.game.character_spritesheet.get_sprite(17, 103, self.width, self.height),
            self.game.character_spritesheet.get_sprite(33, 102, self.width, self.height),
            self.game.character_spritesheet.get_sprite(49, 103, self.width, self.height),
        ]

        right_animations = [
            self.game.character_spritesheet.get_sprite(2, 38, self.width, self.height),
            self.game.character_spritesheet.get_sprite(18, 39, self.width, self.height),
            self.game.character_spritesheet.get_sprite(34, 38, self.width, self.height),
            self.game.character_spritesheet.get_sprite(50, 39, self.width, self.height),
        ]

        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(1, 6, self.width, self.height)
            else:
                self.image = down_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1

        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(0, 69, self.width, self.height)
            else:
                self.image = up_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1

        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(1, 102, self.width, self.height)
            else:
                self.image = left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1

        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(2, 38, self.width, self.height)
            else:
                self.image = right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1

class Item(Sprites):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self._layer = ITEM_LAYER
        self.groups = self.game.all_sprites, self.game.items
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = ITEM_WIDTH*2
        self.height = ITEM_HEIGHT*2

        self.image = pygame.image.load('img/items.png')
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        print(self.rect)
        self.rect.x = self.game.player.x-18
        self.rect.y = self.game.player.y-10
        self.rotate()

    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.x, mouse_y - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

        self.image = pygame.transform.rotate(pygame.image.load('img/items.png'), int(angle))
        self.image.set_colorkey(BLACK)

class Enemy(Sprites):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT

        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.animation_loop = 1

        self.image = self.game.enemy_spritesheet.get_sprite(4, 7, self.width-4, self.height)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.move_towards_player(self.game.player)
        self.animate()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def move_towards_player(self, player):
        if self.rect.x > player.rect.x:
            self.x_change -= ENEMY_SPEED
            self.facing = 'left'
        elif self.rect.x < player.rect.x:
            self.x_change += ENEMY_SPEED
            self.facing = 'right'

        if self.rect.y < player.rect.y:
            self.y_change += ENEMY_SPEED
            self.facing = 'down'
        elif self.rect.y > player.rect.y:
            self.y_change -= ENEMY_SPEED
            self.facing = 'up'

    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if direction == 'x':
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right

        if direction == 'y':
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom



    def animate(self):
        down_animations = [
            self.game.enemy_spritesheet.get_sprite(4, 7, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(37, 8, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(68, 7, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(101, 8, self.width, self.height),
        ]

        up_animations = [
            self.game.enemy_spritesheet.get_sprite(7, 39, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(39, 40, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(71, 39, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(104, 40, self.width, self.height),
        ]

        left_animations = [
            self.game.enemy_spritesheet.get_sprite(10, 101, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(42, 102, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(74, 101, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(106, 102, self.width, self.height),
        ]

        right_animations = [
            self.game.enemy_spritesheet.get_sprite(10, 69, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(42, 70, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(74, 69, self.width, self.height),
            self.game.enemy_spritesheet.get_sprite(106, 70, self.width, self.height),
        ]

        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(1, 6, self.width, self.height)
            else:
                self.image = down_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1

        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(0, 69, self.width, self.height)
            else:
                self.image = up_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1

        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(10, 101, self.width, self.height)
            else:
                self.image = left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1

        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(10, 69, self.width, self.height)
            else:
                self.image = right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 4:
                    self.animation_loop = 1


class Block(Sprites):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        

        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(112, 81, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(Sprites):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(0, 0, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

