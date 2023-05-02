import pygame

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y, item_boxes, TILE_SIZE):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self,screen_scroll, player):
            self.rect.x += screen_scroll
            #checa se o jogador pegou a caixa
            if pygame.sprite.collide_rect(self, player):

                if self.item_type == 'Health':
                    player.health += 25
                    if player.health > player.max_health:
                        player.health = player.max_health
                elif self.item_type == 'Ammo':
                    player.ammo += 15
                elif self.item_type == 'Grenade':
                    player.grenades += 3
                elif self.item_type == 'Boldrini':
                    player.speed = 1
                elif self.item_type == 'Cloud':
                    player.speed += 2 
                    
                self.kill()