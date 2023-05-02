import pygame
from pygame import mixer
import csv
import button
from classes.Soldier import Soldier
from classes.World import World
from classes.HealthBar import HealthBar
from classes.ScreenFade import ScreenFade 
from classes.Grenade import Grenade

mixer.init()
pygame.init()


screen_width = 800
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('unnamed')

clock = pygame.time.Clock()
FPS = 60
GRAVITY = 0.75
SCROLL_THRESH = 200
TILE_SIZE = 40
ROWS = 16
COLS = 150
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1   
start_game = False 
start_intro = False

moving_left = False
moving_right = False
shoot = False 
grenade = False
grenade_tick = False

#load music and sounds
pygame.mixer.music.load('audio/music.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)

# button imgs
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

# load images
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()


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
PINK = (235, 65, 54)

font = pygame.font.SysFont("Futura", 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x*width)- bg_scroll * 0.5,0))
        screen.blit(mountain_img, ((x*width) - bg_scroll * 0.6, screen_height - mountain_img.get_height()-300))
        screen.blit(pine1_img, ((x*width) - bg_scroll * 0.7, screen_height - pine1_img.get_height()-150))
        screen.blit(pine2_img, ((x*width) - bg_scroll * 0.8, screen_height - pine2_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    
    return data
       
# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 6)

# create buttons
start_button = button.Button(screen_width//2-130, screen_height//2-150, start_img, 1)
exit_button = button.Button(screen_width//2-110, screen_height//2+50, exit_img, 1)
restart_button = button.Button(screen_width//2-100, screen_height//2 - 50, restart_img, 2)


#create sprites groups
enemy_group = pygame.sprite.Group()
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
player, health_bar = world.process_data(world_data, img_list, TILE_SIZE, water_group, decoration_group, Soldier, HealthBar, enemy_group, item_boxes, item_box_group, exit_group)

run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        # draw a menu
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
        pass
    else:
        #update background
        draw_bg()
        #draw world map
        world.draw(screen_scroll, screen)
        #vida do jogador
        health_bar.draw(player.health, screen, BLACK, RED, GREEN)
        
        #Mostra na tela munição, granadas e vida
        draw_text(f"AMMO: {player.ammo}", font, WHITE, 10, 35)
        draw_text(f"GRENADES: {player.grenades}", font, WHITE, 10, 60)

        #Número da VIDA
        # draw_text(f"{player.health}", font, WHITE, 165, 10)
        #Decidir se deixa numero, imagem ou os dois
        for x in range (player.ammo):
            screen.blit(bullet_img, (120 + (x * 10), 40))
        for x in range (player.grenades): 
            screen.blit(grenade_img, (165 + (x * 15), 60))
        draw_text(f"SPEED: {player.speed}", font, WHITE, 10, 85)


        player.update()
        screen = player.draw(screen)

        for enemy in enemy_group:
            player, TILE_SIZE, screen_scroll = enemy.ia(player, TILE_SIZE, screen_scroll, world , bullet_group, shot_fx, bullet_img)
            enemy.update()
            screen = enemy.draw(screen)


        #update and draw groups
        bullet_group.update(screen_scroll, screen_width, world, player, bullet_group, enemy_group)
        bullet_group.draw(screen)
        grenade_group.update(GRAVITY, world, screen_scroll, grenade_fx, explosion_group, player, TILE_SIZE, enemy_group)
        grenade_group.draw(screen)
        explosion_group.update(screen_scroll)
        explosion_group.draw(screen)
        decoration_group.update(screen_scroll)
        water_group.update(screen_scroll)
        exit_group.update(screen_scroll)
        item_box_group.update(screen_scroll, player)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        #show intro
        if start_intro:
            if intro_fade.fade(screen, screen_width, screen_height):
                start_intro = False
                intro_fade.fade_counter = 0
        

        #update player's action
        if player.alive:
            if shoot:
                Bullet, bullet_group, shot_fx = player.shoot(bullet_group, shot_fx, bullet_img)
            elif grenade and not grenade_tick and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (player.rect.size[0] * player.direction * 0.2), player.rect.centery + (player.rect.size[1] * -0.3 ), player.direction, grenade_img)
                grenade_group.add(grenade)
                grenade_tick = True
                player.grenades -= 1
            if player.in_air:
                player.update_action(2) #jump
            elif moving_left or moving_right:
                player.update_action(1) #run
            else:
                player.update_action(0) #idled
            screen_scroll, level_complete, GRAVITY, world, water_group, exit_group, screen_height, screen_width, SCROLL_THRESH, bg_scroll, TILE_SIZE = player.move(moving_left, moving_right, GRAVITY, world, water_group, exit_group, screen_height, screen_width, SCROLL_THRESH, bg_scroll, TILE_SIZE)
            bg_scroll -= screen_scroll
            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data, img_list, TILE_SIZE, water_group, decoration_group, Soldier, HealthBar, enemy_group,item_boxes, item_box_group, exit_group)


        else:
            screen_scroll = 0
            if death_fade.fade(screen, screen_width, screen_height):
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    reset_level()
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data, img_list, TILE_SIZE, water_group, decoration_group, Soldier, HealthBar, enemy_group, item_boxes, item_box_group, exit_group)



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
                jump_fx.play()
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