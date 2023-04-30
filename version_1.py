import pygame
import os
import random
import csv

pygame.init()


screen_width = 800
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('unnamed')

clock = pygame.time.Clock()
FPS = 60
GRAVITY = 0.75
TILE_SIZE = 40
ROWS = 16
COLS = 150
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 21
level = 1

moving_left = False
moving_right = False
shoot = False 
grenade = False
grenade_tick = False


#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#load bullet images
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

#coletaveis
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
boldrini_img = pygame.image.load("img/icons/boldrini.png").convert_alpha()
cloud_img = pygame.image.load("img/icons/cloud.png").convert_alpha()
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img,
    'Boldrini'  : boldrini_img,
    'Cloud'     : cloud_img  
}

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("Futura", 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (screen_width, 300))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades=0):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.grenades = grenades
        self.start_grenades = grenades
        self.ammo = ammo #Munição
        self.start_ammo = ammo
        self.health = 100
        self.max_health = self.health
        self.shoot_cooldown = 0
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #variaveis dos inimigos
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0

        #load all images 
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count the images in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        

    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True


        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y


        #check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy
    

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            #mudei o valor de 0.6 para 0.75 para impedir que o player tome dano do próprio tiro
            bullet_group.add(bullet)
            self.ammo -= 1
    

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) #parado
                self.idling = True
                self.idling_counter = 50
            #verifica se o jogador está na visão do inimigo
            if self.vision.colliderect(player.rect):
                #para o movimento para atirar no jogador
                self.update_action(0) #parado
                self.shoot()
                 
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) #animação do inimigo
                    self.move_counter += 1
                    #visão do inimigo
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    #MOSTRA VISAO INIMIGO: pygame.draw.rect(screen, RED, self.vision)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #loop the animation
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:    
                self.frame_index = 0


    def update_action(self, new_action):
        #check if the new action is different
        if new_action != self.action:
            self.action = new_action
            #update animation settings 
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)
        


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x*TILE_SIZE, y*TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: #create player
                        player = Soldier('player', x*TILE_SIZE, y*TILE_SIZE, 1.7, 5, 20, 10)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        enemy = Soldier('enemy', x*TILE_SIZE, y*TILE_SIZE, 1.6, 2, 20)
                        group_enemys.add(enemy) 
                    elif tile == 17:#create ammo box
                        item_box = ItemBox('Ammo', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:#create grenade box
                        item_box = ItemBox('Grenade', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:#create health box
                        item_box = ItemBox('Health', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:#create exit
                        exit = Exit(img, x*TILE_SIZE, y*TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x * TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x * TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x * TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

#Para adicionar um novo item no mapa, primeiramente temos que chamar importar a imagem lá em cima dessa maneira:
#   nome_item_img = pygame.image.load('img/icons/nome-item.png').convert_alpha()"
#Depois temos que atribuir um nome a ele dentro do dicionário ITEM_BOXES dessa maneira:
#   'nome-item': nome_item_img
#Dentro da classe ItemBox no método update, definimos o que acontece se o player encostar no item, basta adicionar um elif. (Se tiver dando erro, copia o elif de cima e cola embaixo, depois muda o nome do item. Não sei que problema foi esse)
#Depois, abaixo de "create item boxes", temos que criar uma variável para o item, dessa maneira e adiciona-lo ao grupo de sprites item_box_group:
#   nome_item = ItemBox('nome-item', x, y)
#   item_box_group.add(nome_item)
#Por fim, se quiser que um contador do item apareça na tela, basta usar a função draw_text() no loop do jogo dessa maneira, por exemplo:
#   draw_text('x 5', font, WHITE, 35, 15)

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
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

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    
    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
 
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    
    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > screen_width - 100:
            self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                print(player.health)
                self.kill()

        for enemy in group_enemys:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if player.alive:
                    enemy.health -= 25
                    print(enemy.health)
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 90
        self.vel_y = -12
        self.speed = 10
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #Colision grenade
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom

            #Slicing grenade
            self.speed -= 1.6
            if self.speed <= 0:
                self.speed = 0

        if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
            self.direction *= -1
            dx = self.direction * self.speed

        #move grenade
        self.rect.x += dx
        self.rect.y += dy

        self.timer -= 1

        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)

            #damage explosion
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
                print(f"Vida do player - {player.health}")

            for enemy in group_enemys:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                    print(f"Vida do inimigo - {enemy.health}")
            
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4

        #update
        self.counter += 1
        
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

#create sprites groups
group_enemys = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

    clock.tick(FPS)

    #update background
    draw_bg()
    #draw world map
    world.draw()
    #vida do jogador
    health_bar.draw(player.health)
     
    #Mostra na tela munição, granadas e vida
    draw_text(f"AMMO: {player.ammo}", font, WHITE, 10, 35)
    draw_text(f"GRENADES: {player.grenades}", font, WHITE, 10, 60)
    #Número da VIDA
    draw_text(f"{player.health}", font, WHITE, 165, 10)
    #Decidir se deixa numero, imagem ou os dois
    for x in range (player.ammo):
        screen.blit(bullet_img, (120 + (x * 10), 40))
    for x in range (player.grenades): 
        screen.blit(grenade_img, (165 + (x * 15), 60))
    draw_text(f"SPEED: {player.speed}", font, WHITE, 10, 85)


    player.update()
    player.draw()

    for enemy in group_enemys:
        enemy.ai()
        enemy.update()
        enemy.draw()


    #update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)
    grenade_group.update()
    grenade_group.draw(screen)
    explosion_group.update()
    explosion_group.draw(screen)
    decoration_group.update()
    water_group.update()
    exit_group.update()

    item_box_group.update()
    item_box_group.draw(screen)
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)
     

    #update player's action
    if player.alive:
        if shoot:
            player.shoot()
        elif grenade and not grenade_tick and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (player.rect.size[0] * player.direction * 0.2), player.rect.centery + (player.rect.size[1] * -0.3 ), player.direction)
            grenade_group.add(grenade)
            grenade_tick = True
            player.grenades -= 1
            print(player.grenades)
        if player.in_air:
            player.update_action(2) #jump
        elif moving_left or moving_right:
            player.update_action(1) #run
        else:
            player.update_action(0) #idled
        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_r:
                run = False
                run = True
        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_tick = False

    pygame.display.update()

pygame.quit()