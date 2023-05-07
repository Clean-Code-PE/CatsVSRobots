import pygame
from pygame import mixer
import csv
import classes.button as button
from classes.Soldier import Soldier
from classes.World import World
from classes.HealthBar import HealthBar
from classes.ScreenFade import ScreenFade 
from classes.Grenade import Grenade

icon = pygame.image.load('./img/icons/icon.png') 
pygame.display.set_icon(icon)

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
pygame.mixer.music.set_volume(0.08)
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

# imagens do background
clouds_front_img = pygame.image.load('img/background/clouds_front.png').convert_alpha()
clouds_mid_img = pygame.image.load('img/background/clouds_mid.png').convert_alpha()
far_mountains_img = pygame.image.load('img/background/far_mountains.png').convert_alpha()
grassy_mountains_img = pygame.image.load('img/background/grassy_mountains.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky.png').convert_alpha()

# redimensionamento das imagens do background
escala = 2
clouds_front_img = pygame.transform.smoothscale(clouds_front_img, (int(clouds_front_img.get_width()*escala), int(clouds_front_img.get_height()*escala)))
clouds_mid_img = pygame.transform.smoothscale(clouds_mid_img, (int(clouds_mid_img.get_width()*escala), int(clouds_mid_img.get_height()*escala)))
far_mountains_img = pygame.transform.smoothscale(far_mountains_img, (int(far_mountains_img.get_width()*escala), int(far_mountains_img.get_height()*escala)))
grassy_mountains_img = pygame.transform.smoothscale(grassy_mountains_img, (int(grassy_mountains_img.get_width()*escala), int(grassy_mountains_img.get_height()*escala)))
sky_img = pygame.transform.smoothscale(sky_img, (int(sky_img.get_width()*escala), int(sky_img.get_height()*escala)))

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#interface
heart = pygame.image.load('img/icons/heart-1.png.png').convert_alpha()
background_interface = pygame.image.load('img/icons/background-interface.png').convert_alpha()

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
# constantes com codigo de cores 
BG = (126, 76, 67)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

font = pygame.font.SysFont("Futura", 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))
# funçao que carrega as imagens de background e define a velocidade de cada uma
def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(20):
        screen.blit(sky_img, ((x*width)- bg_scroll * 0.5,0))
        screen.blit(far_mountains_img, ((x*width) - bg_scroll * 0.6, screen_height - far_mountains_img.get_height()-50))
        screen.blit(grassy_mountains_img, ((x*width) - bg_scroll * 0.7, screen_height - grassy_mountains_img.get_height()-30))
        screen.blit(clouds_mid_img, ((x*width) - bg_scroll * 0.8, screen_height - clouds_mid_img.get_height()-20))
        screen.blit(clouds_front_img, ((x*width) - bg_scroll * 0.8, screen_height - clouds_front_img.get_height()))

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
start_button = button.Button(screen_width//2-180, screen_height//2-200, start_img, 1.5)
exit_button = button.Button(screen_width//2-173, screen_height//2+50, exit_img, 1.4)
restart_button = button.Button(screen_width//2-160, screen_height//2 - 100, restart_img, 1.3) 


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
# while loop que termina quando o jogo é finalizado ou quando o jogador fecha a aba
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
        #health_bar.draw(player.health, screen, BLACK, RED, GREEN)
        screen.blit(background_interface, (10, 10))
        #Mostra na tela munição, granadas e vida
        draw_text(f"Munição: {player.ammo}", font, WHITE, 26, 55)
        draw_text(f"Granadas: {player.grenades}", font, WHITE, 26, 86)

        #Número da VIDA
        # draw_text(f"{player.health}", font, WHITE, 165, 10)
        for i in range(player.health):
            screen.blit(heart, (35 + (i * 17), 25))
        #Decidir se deixa numero, imagem ou os dois
        # for x in range (player.ammo):
        #     screen.blit(bullet_img, (120 + (x * 10), 40))
        # for x in range (player.grenades): 
        #     screen.blit(grenade_img, (165 + (x * 15), 60))
        #draw_text(f"SPEED: {player.speed}", font, WHITE, 10, 85)


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
                if level > 3:
                    run = False
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
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_z:
                shoot = True
            if event.key == pygame.K_x:
                grenade = True
            if event.key == pygame.K_UP and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_r:
                run = False
                run = True
        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_z:
                shoot = False
            if event.key == pygame.K_x:
                grenade = False
                grenade_tick = False

    pygame.display.update()

pygame.quit()
