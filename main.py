import pygame
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from os import walk
from os.path import join
import os
print(os.getcwd())

from random import randint, choice

class Game:
    def __init__(self):
        pygame.init()
        #setup
        self.display_surface = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Running man")
        self.clock = pygame.time.Clock()
        self.running = True

        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        #gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100

        #enemies timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_position = []

        #audio
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.music = pygame.mixer.Sound(join('audio', 'music.wav'))
        self.music.set_volume(0.3)
        self.music.play(loops= -1)

        #setup
        self.load_images()
        self.setup()    

    def load_images(self):
        self.bullet_surf = pygame.image.load(
            join('images', 'gun', 'bullet.png')
        ).convert_alpha()

        self.enemy_frames = {}

        enemy_path = join('images', 'enemies')

        if not os.path.exists(enemy_path):
            print("ERROR: images/enemies folder does not exist")
            return

        for root, folders, _ in walk(enemy_path):
            for folder in folders:
                self.enemy_frames[folder] = []

                for _, _, file_names in walk(join(enemy_path, folder)):
                    for file_name in sorted(
                        file_names,
                        key=lambda name: int(name.split('.')[0])):
                        full_path = join(enemy_path, folder, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.enemy_frames[folder].append(surf)

            break  # IMPORTANT: only read top-level folders

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center
            Bullet(
                self.bullet_surf, pos, self.gun.direction,(self.all_sprites, self.bullet_sprites))
                
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()


    def gun_timer(self):
        if not self.can_shoot:
            if pygame.time.get_ticks() - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx'))

        for x, y, image in tmx_map.get_layer_by_name('Ground').tiles():
            Sprite((x * tile_size, y * tile_size), image, self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Collisions'):
            CollisionSprite(
                (obj.x, obj.y),
                pygame.Surface((int(obj.width), int(obj.height))), self.collision_sprites)

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((500, 300), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_position.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False

    def run(self):
        while self.running:
            #dt
            dt = self.clock.tick(60) / 1000

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event and self.spawn_position:
                    Enemy(
                        choice(self.spawn_position),choice(list(self.enemy_frames.values())),(self.all_sprites, self.enemy_sprites),self.player,self.collision_sprites)

            #update
            self.input()
            self.gun_timer()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()

            #draw
            self.display_surface.fill("black")
            offset = pygame.Vector2(self.player.rect.center) - pygame.Vector2(
                window_width // 2, window_height // 2
            )

            self.all_sprites.draw(self.display_surface, offset)
            pygame.display.update()


if __name__ == "__main__":
    Game().run()
    pygame.quit()
