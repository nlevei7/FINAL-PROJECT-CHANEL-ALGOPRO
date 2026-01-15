from settings import *
import pygame
from math import atan2, degrees


# ---------------- BASIC TILE SPRITE ----------------
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


# ---------------- GUN ----------------
class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)

        self.player = player
        self.distance = 140
        self.direction = pygame.Vector2(0, 1)

        self.gun_surf = pygame.image.load(
            join('images', 'gun', 'gun.png')
        ).convert_alpha()

        self.image = self.gun_surf
        self.rect = self.image.get_rect()

    def update(self, dt):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        screen_center = pygame.Vector2(window_width // 2, window_height // 2)

        direction = mouse_pos - screen_center
        if direction.length() != 0:
            self.direction = direction.normalize()

        angle = degrees(atan2(self.direction.x, self.direction.y)) - 90
        self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)

        self.rect.center = self.player.rect.center + self.direction * self.distance


# ---------------- BULLET ----------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)

        self.direction = direction
        self.speed = 1200
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


# ---------------- ENEMY ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)

        self.player = player
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 6

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)

        self.speed = 180

        self.death_time = 0
        self.death_duration = 300

    def destroy(self):
        if self.death_time == 0:
            self.death_time = pygame.time.get_ticks()
            surf = pygame.mask.from_surface(self.image).to_surface()
            surf.set_colorkey((0, 0, 0))
            self.image = surf

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def update(self, dt):
        # if dead → only run death timer
        if self.death_time != 0:
            self.death_timer()
            return

        # move toward player
        direction = pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length() != 0:
            direction = direction.normalize()

        self.rect.center += direction * self.speed * dt

        # animate
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
