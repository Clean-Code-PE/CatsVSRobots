import pygame

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0
    
    def fade(self, screen, screen_width, screen_height):
        fade_complete = False
        self.fade_counter += self.speed
        
        if self.direction == 1:
            pygame.draw.rect(screen, self.colour, (0- self.fade_counter,0, screen_width//2, screen_height))
            pygame.draw.rect(screen, self.colour, (screen_width//2 + self.fade_counter,0, screen_width, screen_height))
            pygame.draw.rect(screen, self.colour, (0, 0- self.fade_counter, screen_width, screen_height//2))
            pygame.draw.rect(screen, self.colour, (0 , screen_height//2 + self.fade_counter, screen_width, screen_height//2))
        # vertical screen fade down
        elif self.direction == 2:
            pygame.draw.rect(screen, self.colour, (0,0, screen_width, 0 + self.fade_counter))
        
        if self.fade_counter >= screen_width:
            fade_complete = True 

        return fade_complete 