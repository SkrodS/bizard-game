import pygame
from config import *
from gamestate import *
import math
import random

class Spritesheet:
    '''
    En bild med flera sprites
    '''
    def __init__(self, file):
        self.__sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        '''
        Hämtar sprite (bild) från ett spritesheet
        '''
        sprite = pygame.Surface([width, height])
        sprite.blit(self.__sheet, (0,0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite

class ScreenItem(pygame.sprite.Sprite):
    '''
    Sprite som inte byter x eller y värde.
    '''
    def __init__(self, game, x, y, width, height, layer):
        self.game = game

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self._layer = layer

        self.width = width
        self.height = height

class MovingScreenItem(ScreenItem):
    '''
    En sprite som kan röra på sig
    '''
    def __init__(self, game, x, y, width, height, layer):
        super().__init__(game, x, y, width, height, layer)

        self.x_change = 0
        self.y_change = 0

        self.animation_loop = 1
        self.facing = 'down'

        self.collision_immune = False
        self.collision_time = 0


class Player(MovingScreenItem):
    '''
    Spelarens karaktär. Innehåller alla scores samt HUD:en. Ärver från Sprite()
    '''
    def __init__(self, game, x, y, bunny):
        super().__init__(game, x, y, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_LAYER)
        self.__groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.__health = 1
        self.__target_health = 3
        self.__max_health = 3
        self.__health_bar_length = 100
        self.__health_ratio = self.__max_health / self.__health_bar_length
        self.__health_change_speed = 0.03

        self.__shoot_cooldown = False
        self.__shoot_time = 0

        self.__heal_cooldown = False
        self.__heal_time = 0

        self.__enemeis = len(self.game.enemies)

        self.kills = 0
        self.bunny = bunny

        self.image = self.game.character_spritesheet.get_sprite(1, 6, self.width-3, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        '''
        Kör Player()-funktionerna som ska köras varje tick
        '''
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

        self.check_win()

    def health_bar(self):
        '''
        Ritar HP-indikatorn på skärmen
        '''
        transition_width = 0
        transition_color = (255,0,0)

        if self.__health < self.__target_health:
            self.__health += self.__health_change_speed
            transition_width = int((self.__target_health - self.__health) / self.__health_ratio)
            transition_color = GREEN

        if self.__health > self.__target_health:
            self.__health -= self.__health_change_speed 
            transition_width = int((self.__target_health - self.__health) / self.__health_ratio)
            transition_color = YELLOW

        health_bar_width = int(self.__health / self.__health_ratio)
        health_bar = pygame.Rect(5,13,health_bar_width,8)
        transition_bar = pygame.Rect(health_bar.right,13,transition_width,8)
		
        pygame.draw.rect(self.game.screen,BLACK,(0,0,WIN_WIDTH,24))
        pygame.draw.rect(self.game.screen,BLACK,(5,13,self.__health_bar_length,8))
        pygame.draw.rect(self.game.screen,RED,health_bar)
        pygame.draw.rect(self.game.screen,transition_color,transition_bar)	
        pygame.draw.rect(self.game.screen,WHITE,(5,13,self.__health_bar_length,8),1)

        text = self.game.font.render('Health', True, WHITE)
        text_rect = text.get_rect()
        text_rect.x = 8
        self.game.screen.blit(text, text_rect)

    def check_win(self):
        '''
        Kollar om alla fiender är döda
        '''
        if self.kills == self.__enemeis:
            self.__target_health = self.__max_health
            self.game.bunny = self.bunny
            self.collision_immune = True
            pygame.mixer.Sound('music/535840__evretro__8-bit-mini-win-sound-effect.wav').play()
            self.game.gamestate = Gamestate.NEXT_WAVE

    def display_hud(self):
        '''
        Ritar HUD:en
        '''
        text = self.game.font.render(f'x{self.bunny}', False, YELLOW)
        text_rect = text.get_rect()
        text_rect.x = WIN_WIDTH-27
        text_rect.y = 7

        bunny_image = pygame.transform.smoothscale(pygame.image.load('img/bunnysheet5.png').convert_alpha(), (20, 20))
        bunny_rect = bunny_image.get_rect()
        bunny_rect.x = WIN_WIDTH-50
        bunny_rect.y = 2

        if self.__enemeis < len(self.game.enemies):
            self.__enemeis = len(self.game.enemies)

        enemies_image = pygame.image.load('img/log_still.png').convert_alpha()
        enemies_rect = enemies_image.get_rect()
        enemies_rect.x = (WIN_WIDTH/2)+30
        enemies_rect.y = 3

        text_enemies = self.game.font.render(f'{self.kills}/{self.__enemeis}', False, YELLOW)
        text_enemies_rect = text_enemies.get_rect()
        text_enemies_rect.x = (WIN_WIDTH/2)+52
        text_enemies_rect.y = 7

        text_wave = self.game.font.render(f'Wave: {self.game.wave}', False, PURPLE)
        text_wave_rect = text_wave.get_rect()
        text_wave_rect.x = (WIN_WIDTH/2-40)
        text_wave_rect.y = 7
        
        self.game.screen.blit(text_wave, text_wave_rect)
        self.game.screen.blit(text, text_rect)
        self.game.screen.blit(bunny_image, bunny_rect)
        self.game.screen.blit(text_enemies, text_enemies_rect)
        self.game.screen.blit(enemies_image, enemies_rect)

    def movement(self):
        '''
        Kontrollerar spelaren (rörelse(W,A,S,D), avfyra skott(L_MOUSE eller SPACE), paus(ESCAPE), använda en kanin(R_MOUSE eller L_SHIFT))
        '''
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed(num_buttons=3)

        # Kontroller för att heal:a sig
        if pygame.time.get_ticks() - self.__heal_time > 300:
            self.__heal_cooldown = False
        if self.bunny > 0 and self.__target_health != self.__max_health:
            if keys[pygame.K_LSHIFT] and not self.__heal_cooldown or mouse[2] and not self.__heal_cooldown:                
                pygame.mixer.Sound('music/270304__littlerobotsoundfactory__collect-point-00.wav').play()
                self.__heal_time = pygame.time.get_ticks()
                self.__heal_cooldown = True
                self.bunny -= 1
                self.get_health(0.5)

        # Kontroller för att skjuta
        if pygame.time.get_ticks() - self.__shoot_time > 300:
            self.__shoot_cooldown = False
        if mouse[0] and not self.__shoot_cooldown or keys[pygame.K_SPACE] and not self.__shoot_cooldown:
            pygame.mixer.Sound('music/270343__littlerobotsoundfactory__shoot-01.wav').play()
            self.__shoot_time = pygame.time.get_ticks()
            self.__shoot_cooldown = True
            Bullet(self.game, 0, 0)
        
        # Kontroller för att röra sig
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

        # Kontroller för att pausa
        if keys[pygame.K_ESCAPE]:
            self.game.gamestate = Gamestate.PAUSED

    def get_health(self, amount):
        '''
        Ger spelaren liv
        '''
        if self.__target_health < self.__max_health:
            self.__target_health += amount

        if self.__target_health > self.__max_health:
            self.__target_health = self.__max_health

    def collide_enemy(self):
        '''
        Kollar om spelaren kolliderar med en fiende och delar ut skada om det händer
        '''
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)

        if pygame.time.get_ticks() - self.collision_time > 1000:
            self.collision_immune = False

        if hits and not self.collision_immune:
            pygame.mixer.Sound('music/170635__swedger__fami-crash.wav').play()
            self.__target_health -= 1
            self.collision_immune = True
            self.collision_time = pygame.time.get_ticks()
            self.game.screen.fill(RED)

        if self.__target_health <= 0:
            self.kill()
            self.game.gamestate = Gamestate.GAME_OVER

    def collide_blocks(self, direction):
        '''
        Kollar om spelaren kolliderar med ett block och stannar spelaren om det sker
        '''
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
        '''
        Animerar spelarens sprite
        '''
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

class Item(ScreenItem):
    '''
    Spelarens trollstav
    '''
    def __init__(self, game, x, y):
        super().__init__(game, x, y, ITEM_WIDTH*2, ITEM_HEIGHT*2, ITEM_LAYER)
        self.__groups = self.game.all_sprites, self.game.items
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.image = pygame.image.load('img/items.png')
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        '''
        Kör alla item()-funktioner som ska köras varje tick
        '''
        self.rotate()

    def rotate(self):
        '''
        Roterar item så att den pekar mot musen
        '''
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.game.player.rect.centerx, mouse_y - self.game.player.rect.centery
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

        image_copy = pygame.transform.rotate(pygame.image.load('img/items.png'), int(angle)-135)
        self.image = image_copy
        self.rect.x = self.game.player.rect.centerx - int(image_copy.get_width() / 2)
        self.rect.y = self.game.player.rect.centery - int(image_copy.get_height() / 2)

class Bullet(MovingScreenItem):
    '''
    Skott
    '''
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 15, 15, ITEM_LAYER)
        self.__groups = self.game.all_sprites, self.game.bullets
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.image = self.game.bullet_spritesheet.get_sprite(107, 330, self.width, self.height)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.game.player.rect.x
        self.rect.y = self.game.player.rect.centery-10

        mx, my = pygame.mouse.get_pos()
        self.__dir = (mx - self.rect.x, my - self.rect.y)

        length = math.hypot(*self.__dir)

        if length == 0.0:
            self.__dir = (0, -1)
        else:
            self.__dir = (self.__dir[0]/length, self.__dir[1]/length)

    def update(self):
        '''
        Kör alla Bullet()-funktioner som ska köras varje tick
        '''
        self.animate()
        self.move()
        self.collide()

    def move(self):
        '''
        Rör skottet i musens riktning i förhållande till mitten av player
        '''
        self.rect.x = self.rect.x + self.__dir[0] * 4
        self.rect.y = self.rect.y + self.__dir[1] * 4

    def collide(self):
        '''
        Kollar om skottet kolliderar med ett block och raderar skottet om det sker
        '''
        hits_blocks = pygame.sprite.spritecollide(self, self.game.blocks, False)

        if hits_blocks:
            pygame.mixer.Sound('music/270338__littlerobotsoundfactory__open-01.wav').play()
            self.kill()

    def animate(self):
        '''
        Animerar skottet sprite
        '''
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

class Enemy(MovingScreenItem):
    '''
    Fiende
    '''
    def __init__(self, game, x, y):
        super().__init__(game, x, y, ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_LAYER)
        self.__groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.__health = self.game.difficulty

        self.image = self.game.enemy_spritesheet.get_sprite(4, 7, self.width-4, self.height)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        '''
        Kör alla Enemy()-funktioner som ska köras varje tick
        '''
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
        '''
        Rör fienden mot spelaren
        '''
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
        '''
        Kollar om fienden kolliderar med ett block och stoppar fienden om det sker
        '''
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
        '''
        Kollar om fienden kolliderar med ett skott och raderar fienden om det sker
        '''
        hits = pygame.sprite.spritecollide(self, self.game.bullets, True)

        if pygame.time.get_ticks() - self.collision_time > 300:
            self.collision_immune = False

        if hits and not self.collision_immune:
            pygame.mixer.Sound('music/270338__littlerobotsoundfactory__open-01.wav').play()
            self.__health -= 1
            self.collision_immune = True
            self.collision_time = pygame.time.get_ticks()

        if self.__health <= 0:
            self.game.player.bunny += 1
            self.game.player.kills += 1
            self.kill()

    def animate(self):
        '''
        Animerar fiendens sprite
        '''
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

class Block(ScreenItem):
    '''
    Block-tile
    '''
    def __init__(self, game, x, y):
        super().__init__(game, x, y, TILESIZE, TILESIZE, BLOCK_LAYER)
        self.__groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.image = self.game.terrain_spritesheet.get_sprite(112, 81, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(ScreenItem):
    '''
    Ground-tile
    '''
    def __init__(self, game, x, y):
        super().__init__(game, x, y, TILESIZE, TILESIZE, GROUND_LAYER)
        self.__groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.image = self.game.terrain_spritesheet.get_sprite(0, 0, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Button(ScreenItem):
    '''
    Knapp
    '''
    def __init__(self, game, x, y, text, color, hover_color, action):
        super().__init__(game, x, y, 0, 0, MENU_LAYER)
        self.__groups = self.game.menu, self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.__text = text
        self.__color = color
        self.__hover_color = hover_color

        self.__action = action

        self.__surface = self.game.font.render(self.__text, False, self.__color)

        self.rect = self.__surface.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.image = self.__surface

    def update(self):
        '''
        Kör alla Button()-funktioner som ska varje tick
        '''
        self.hover()

    def hover(self):
        '''
        Kollar om musen är på knappen och om knappen klickas på
        '''
        mouse = pygame.mouse.get_pressed(num_buttons=3)

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.__surface = self.game.font.render(self.__text, False, self.__hover_color)
            self.image = self.__surface
            if mouse[0] and pygame.time.get_ticks() - self.game.cooldown > 300:
                pygame.mixer.Sound('music/270315__littlerobotsoundfactory__menu-navigate-03.wav').play()
                self.game.gamestate = self.__action
        else:
            self.__surface = self.game.font.render(self.__text, False, self.__color)
            self.image = self.__surface

class Title(ScreenItem):
    '''
    Stor text
    '''
    def __init__(self, game, x, y, text, color):
        super().__init__(game, x, y, 0, 0, MENU_LAYER)
        self.__groups = self.game.menu, self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.__groups)

        self.__text = text
        self.__color = color

        self.__surface = self.game.font_big.render(self.__text, True, self.__color)

        self.rect = self.__surface.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.image = self.__surface