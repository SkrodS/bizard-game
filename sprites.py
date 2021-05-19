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

        self.health = 1
        self.target_health = 3
        self.max_health = 3
        self.health_bar_length = 100
        self.health_ratio = self.max_health / self.health_bar_length
        self.health_change_speed = 0.03

        self.collision_immune = False
        self.collision_time = 0

        self.shoot_cooldown = False
        self.shoot_time = 0

        self.heal_cooldown = False
        self.heal_time = 0

        self.kills = 0
        self.enemeis = len(self.game.enemies)

        self.bunny = 0

        self.image = self.game.character_spritesheet.get_sprite(1, 6, self.width-3, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        # self.get_health(0.0001)
        self.movement()
        self.animate()
        self.collide_enemy()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

        self.health_bar()
        self.display_hud()

    def health_bar(self):
        transition_width = 0
        transition_color = (255,0,0)

        if self.health < self.target_health:
            self.health += self.health_change_speed
            transition_width = int((self.target_health - self.health) / self.health_ratio)
            transition_color = GREEN

        if self.health > self.target_health:
            self.health -= self.health_change_speed 
            transition_width = int((self.target_health - self.health) / self.health_ratio)
            transition_color = YELLOW

        health_bar_width = int(self.health / self.health_ratio)
        health_bar = pygame.Rect(5,13,health_bar_width,8)
        transition_bar = pygame.Rect(health_bar.right,13,transition_width,8)
		
        pygame.draw.rect(self.game.screen,BLACK,(0,0,WIN_WIDTH,24))
        pygame.draw.rect(self.game.screen,BLACK,(5,13,self.health_bar_length,8))
        pygame.draw.rect(self.game.screen,RED,health_bar)
        pygame.draw.rect(self.game.screen,transition_color,transition_bar)	
        pygame.draw.rect(self.game.screen,WHITE,(5,13,self.health_bar_length,8),1)

        text = self.game.font.render('Health', True, WHITE)
        text_rect = text.get_rect()
        text_rect.x = 8
        self.game.screen.blit(text, text_rect)

    def display_hud(self):
        text = self.game.font.render(f'x{self.bunny}', True, YELLOW)
        text_rect = text.get_rect()
        text_rect.x = WIN_WIDTH-17
        text_rect.y = 7

        bunny_image = pygame.transform.smoothscale(pygame.image.load('img/bunnysheet5.png').convert_alpha(), (20, 20))
        bunny_rect = bunny_image.get_rect()
        bunny_rect.x = WIN_WIDTH-40
        bunny_rect.y = 2

        if self.enemeis < len(self.game.enemies):
            self.enemeis = len(self.game.enemies)

        enemies_image = pygame.image.load('img/log_still.png').convert_alpha()
        enemies_rect = enemies_image.get_rect()
        enemies_rect.x = (WIN_WIDTH/2)-10
        enemies_rect.y = 3

        text_enemies = self.game.font.render(f'{self.kills}/{self.enemeis}', True, YELLOW)
        text_enemies_rect = text_enemies.get_rect()
        text_enemies_rect.x = (WIN_WIDTH/2)+12
        text_enemies_rect.y = 7
        
        self.game.screen.blit(text, text_rect)
        self.game.screen.blit(bunny_image, bunny_rect)
        self.game.screen.blit(text_enemies, text_enemies_rect)
        self.game.screen.blit(enemies_image, enemies_rect)

    def movement(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed(num_buttons=3)

        if pygame.time.get_ticks() - self.heal_time > 300:
            self.heal_cooldown = False

        if self.bunny > 0 and self.target_health != self.max_health:
            if keys[pygame.K_LSHIFT] and not self.heal_cooldown or mouse[2] and not self.heal_cooldown:
                self.heal_time = pygame.time.get_ticks()
                self.heal_cooldown = True
                self.bunny -= 1
                self.get_health(0.5)

        if pygame.time.get_ticks() - self.shoot_time > 300:
            self.shoot_cooldown = False

        if mouse[0] and not self.shoot_cooldown or keys[pygame.K_SPACE] and not self.shoot_cooldown:
            self.shoot_time = pygame.time.get_ticks()
            self.shoot_cooldown = True
            Bullet(self.game, 0, 0)
        
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

        if keys[pygame.K_ESCAPE]:
            self.game.playing = False

    def get_health(self, amount):
        if self.target_health < self.max_health:
            self.target_health += amount
        if self.target_health > self.max_health:
            self.target_health = self.max_health

    def collide_enemy(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if pygame.time.get_ticks() - self.collision_time > 1000:
            self.collision_immune = False
        if hits and not self.collision_immune:
            self.target_health -= 1
            self.collision_immune = True
            self.collision_time = pygame.time.get_ticks()
            self.game.screen.fill(RED)
        if self.target_health <= 0:
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
        self.rotate()

    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.game.player.rect.centerx, mouse_y - self.game.player.rect.centery
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

        image_copy = pygame.transform.rotate(pygame.image.load('img/items.png'), int(angle)-135)
        self.image = image_copy
        self.rect.x = self.game.player.rect.centerx - int(image_copy.get_width() / 2)
        self.rect.y = self.game.player.rect.centery - int(image_copy.get_height() / 2)

class Bullet(Sprites):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self._layer = ITEM_LAYER
        self.groups = self.game.all_sprites, self.game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = 15
        self.height = 15

        self.animation_loop = 0

        self.image = self.game.bullet_spritesheet.get_sprite(107, 330, self.width, self.height)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.game.player.rect.x
        self.rect.y = self.game.player.rect.centery-10

        mx, my = pygame.mouse.get_pos()
        self.dir = (mx - self.rect.x, my - self.rect.y)

        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0]/length, self.dir[1]/length)

    def update(self):
        self.animate()
        self.move()
        self.collide()

    def move(self):
        self.rect.x = self.rect.x + self.dir[0] * 4
        self.rect.y = self.rect.y + self.dir[1] * 4

    def collide(self):
        hits_blocks = pygame.sprite.spritecollide(self, self.game.blocks, False)

        if hits_blocks:
            self.kill()

    def animate(self):
        animations = [
            self.game.bullet_spritesheet.get_sprite(107, 330, self.width, self.height),
            self.game.bullet_spritesheet.get_sprite(126, 330, self.width, self.height),
            self.game.bullet_spritesheet.get_sprite(145, 331, self.width, self.height),
            self.game.bullet_spritesheet.get_sprite(165, 329, self.width, self.height),
            self.game.bullet_spritesheet.get_sprite(183, 330, self.width, self.height),
            self.game.bullet_spritesheet.get_sprite(202, 330, self.width, self.height),
            self.game.bullet_spritesheet.get_sprite(221, 331, self.width, self.height),
            self.game.bullet_spritesheet.get_sprite(241, 329, self.width, self.height),
        ]
        self.image = animations[math.floor(self.animation_loop)]
        self.animation_loop += 0.2
        if self.animation_loop >= 8:
            self.animation_loop = 0

class Enemy(Sprites):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT

        self.health = 2
        self.collision_immune = False
        self.collision_time = 0

        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.animation_loop = 1

        self.image = self.game.enemy_spritesheet.get_sprite(4, 7, self.width-4, self.height)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.collide_bullet()
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

    def collide_bullet(self):
        hits = pygame.sprite.spritecollide(self, self.game.bullets, True)
        if pygame.time.get_ticks() - self.collision_time > 300:
            self.collision_immune = False
        if hits and not self.collision_immune:
            self.health -= 1
            self.collision_immune = True
            self.collision_time = pygame.time.get_ticks()
        if self.health <= 0:
            self.game.player.bunny += 1
            self.game.player.kills += 1
            self.kill()

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

        fire_animations = [
            self.game.object_spritesheet.get_sprite(65, 49, 13, 15),
            self.game.object_spritesheet.get_sprite(81, 49, 14, 15),
            self.game.object_spritesheet.get_sprite(97, 50, 14, 14),
            self.game.object_spritesheet.get_sprite(113, 49, 14, 15),
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
        
        if self.collision_immune:
            self.x_change = 0
            self.y_change = 0
            self.image = fire_animations[math.floor(self.animation_loop)]
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

class Button(Sprites):
    def __init__(self, game, x, y, text, color1, color2, action):
        super().__init__(game, x, y)
        self._layer = MENU_LAYER
        self.groups = self.game.menu
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.text = text
        self.color1 = color1
        self.color2 = color2

        self.action = action

        self.surface = self.game.font.render(self.text, False, self.color1)

        self.rect = self.surface.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.image = self.surface

    def update(self):
        self.hover()

    def hover(self):
        mouse = pygame.mouse.get_pressed(num_buttons=3)

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.surface = self.game.font.render(self.text, False, self.color2)
            self.image = self.surface
            if mouse[0]:
                self.action()
        else:
            self.surface = self.game.font.render(self.text, False, self.color1)
            self.image = self.surface

class Title(Sprites):
    def __init__(self, game, x, y, text, color):
        super().__init__(game, x, y)
        self._layer = MENU_LAYER
        self.groups = self.game.menu
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.text = text
        self.color = color

        self.surface = self.game.font_big.render(self.text, True, self.color)

        self.rect = self.surface.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.image = self.surface