import pygame
from classes.Explosion import Explosion

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, grenade_img):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 90
        self.vel_y = -12
        self.speed = 8
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self, GRAVITY, world, screen_scroll, grenade_fx, explosion_group, player, TILE_SIZE, enemy_group):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #verifica a colisão com o mapa
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
        
            #verifica a colisão em y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #colisão com o ambiente
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
        

        #movimentação da granada
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1

        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)

            #dano da explosão
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 3

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 5