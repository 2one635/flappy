import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60
flapping = False
over = False
pgap = 200
pfreq = 1500
last_pipe = pygame.time.get_ticks() - pfreq

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



class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)#
        self.image = pygame.Surface((80, 500))
        self.image.fill((0, 200, 0))
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pgap // 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pgap // 2)]   

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()
        

         

player_group = pygame.sprite.Group()
Bird = Player(100, int(height / 2))
player_group.add(Bird)

pipe_group = pygame.sprite.Group()

run = True
while run:
    clock.tick(fps)
    window.fill((135, 206, 235))
    player_group.update()
    player_group.draw(window)
    
    pipe_group.draw(window)
    pygame.draw.rect(window, (34, 139, 34), (0, ground_y, 864, ground_height))
    pygame.display.update()
    
    if pygame.sprite.groupcollide(player_group, pipe_group, False, False) or Bird.rect.top < 0:
        over = True
        

    if Bird.rect.bottom >= ground_y:
        Bird.rect.top = ground_y
        Bird.vel = 0
        over = True
        flapping = False
    

    if over == False and flapping == True:
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pfreq:
                pheight = random.randint(-100, 100)
                b_pipe = Pipe(width, int(height / 2) + pheight, 1)
                t_pipe = Pipe(width, int(height / 2) + pheight, -1)
                pipe_group.add(b_pipe)
                pipe_group.add(t_pipe)
                last_pipe = time_now

            pipe_group.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flapping == False and over == False:
               flapping = True
            
pygame.quit()