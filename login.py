import pygame
from pygame.locals import *
import database 

pygame.init()

width = 864
height = 936
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy Bird - Login")

clock = pygame.time.Clock()
fps = 60

# Colours
white = (255, 255, 255)
black = (0, 0, 0)
grey = (200, 200, 200)
red = (255, 0, 0)
green = (0, 200, 0)
blue = (135, 206, 235)

username_text = ""
password_text = ""
active_box = None
message = ""
message_colour = red

username_box = pygame.Rect(282, 350, 300, 50)
password_box = pygame.Rect(282, 450, 300, 50)
login_button = pygame.Rect(232, 570, 150, 50)
register_button = pygame.Rect(482, 570, 150, 50)

def draw_login_screen():
    window.fill(blue)
    
    title_font = pygame.font.SysFont("Impact", 80)
    input_font = pygame.font.SysFont("Impact", 40)
    
    title = title_font.render("Flappy Bird", True, white)
    window.blit(title, (250, 150))
    
    pygame.draw.rect(window, white, username_box, border_radius=5)
    pygame.draw.rect(window, black, username_box, 2, border_radius=5)
    username_surface = input_font.render(username_text, True, black)
    window.blit(username_surface, (username_box.x + 10, username_box.y + 10))
    
    pygame.draw.rect(window, white, password_box, border_radius=5)
    pygame.draw.rect(window, black, password_box, 2, border_radius=5)
    password_surface = input_font.render("*" * len(password_text), True, black)
    window.blit(password_surface, (password_box.x + 10, password_box.y + 10))
    
    label_font = pygame.font.SysFont("Impact", 35)
    window.blit(label_font.render("Username:", True, white), (282, 310))
    window.blit(label_font.render("Password:", True, white), (282, 410))
    
    pygame.draw.rect(window, green, login_button, border_radius=5)
    pygame.draw.rect(window, green, register_button, border_radius=5)
    window.blit(label_font.render("Login", True, white), (267, 582))
    window.blit(label_font.render("Register", True, white), (490, 582))
    
    msg_font = pygame.font.SysFont("Impact", 30)
    window.blit(msg_font.render(message, True, message_colour), (282, 650))
    
    pygame.display.update()

def login_screen():
    global username_text, password_text, active_box, message, message_colour
    
    run = True
    while run:
        clock.tick(fps)
        draw_login_screen()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_box.collidepoint(event.pos):
                    active_box = "username"
                elif password_box.collidepoint(event.pos):
                    active_box = "password"
                else:
                    active_box = None
                
                if login_button.collidepoint(event.pos):
                    player = database.login_player(username_text, password_text)
                    if player:
                        message = "Login successful!"
                        message_colour = green
                        pygame.time.wait(1000)
                        return player
                    else:
                        message = "Incorrect username or password!"
                        message_colour = red
                
                if register_button.collidepoint(event.pos):
                    if username_text == "" or password_text == "":
                        message = "Please fill in all fields!"
                        message_colour = red
                    else:
                        success = database.register_player(username_text, password_text)
                        if success:
                            message = "Registration successful! Please login."
                            message_colour = green
                            username_text = ""
                            password_text = ""
                        else:
                            message = "Username already taken!"
                            message_colour = red
            
            if event.type == pygame.KEYDOWN:
                if active_box == "username":
                    if event.key == pygame.K_BACKSPACE:
                        username_text = username_text[:-1]
                    else:
                        username_text += event.unicode
                elif active_box == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password_text = password_text[:-1]
                    else:
                        password_text += event.unicode

if __name__ == "__main__":
    player = login_screen()
    if player:
        import game
        game.start(player)