import pygame

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y, TILE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height() + 2))

    def update(self, screen_scroll):
        self.rect.x += screen_scroll