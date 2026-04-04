import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60
flapping = False
over = False

width = 864
height = 936

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy Bird")

scroll_speed = 4
ground_height = 120
ground_y = height - ground_height


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 15
        size = self.radius * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 0), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0
        self.clicked = False

    def update(self):
        if flapping == True or over == True:
          self.vel += 0.5
          self.rect.y += self.vel
          if self.rect.bottom >= ground_y:
               self.rect.bottom = ground_y
               self.vel = 0

          if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False and over == False:
               self.clicked = True
               self.vel = -10
          if pygame.mouse.get_pressed()[0] == 0:
               self.clicked = False
         

player_group = pygame.sprite.Group()
Bird = Player(100, int(height / 2))
player_group.add(Bird)

run = True
while run:
    clock.tick(fps)
    window.fill((135, 206, 235))
    player_group.update()
    player_group.draw(window)
    pygame.draw.rect(window, (34, 139, 34), (0, ground_y, 864, ground_height))
    pygame.display.update()
    
    if Bird.rect.bottom >= ground_y:
        Bird.rect.top = ground_y
        Bird.vel = 0
        over = True
        flapping = False
    
    if Bird.rect.top <= 0:
     Bird.rect.top = 0
     over = True
     flapping = False    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flapping == False and over == False:
               flapping = True
            
pygame.quit()