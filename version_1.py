import pygame

pygame.init()

screen_width = 800
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('unnamed')

x = 200
y = 200
img = pygame.image.load('img/player/Idle/0.png')
rect = img.get_rect()
rect.center = (x, y)


run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


pygame.quit()
