import pygame
from pygame.locals import *
import random
import database

# Global variables
logged_player = None
clock = None
fps = 60
flapping = False
over = False
pgap = 200
pfreq = 1500
last_pipe = 0
width = 864
height = 936
window = None
font = None
white = (255, 255, 255)
score = 0
pipe_pass = False
scroll_speed = 4
ground_height = 120
ground_y = height - ground_height
player_group = None
Bird = None
pipe_group = None
death_count = 0

# Power-up variables
powerup_group = None
active_powerup = None
powerup_timer = 0
base_scroll_speed = 4
POWERUP_DURATION = 5000
powerup_types = ["slow_motion", "invincibility", "double_score", "shrink_bird"]
powerup_colours = {
    "slow_motion": (255, 255, 0),
    "invincibility": (0, 150, 255),
    "double_score": (255, 0, 0),
    "shrink_bird": (0, 200, 0)
}
powerup_names = {
    "slow_motion": "Slow Motion",
    "invincibility": "Invincibility",
    "double_score": "Double Score",
    "shrink_bird": "Shrink Bird"
}


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 15
        self.original_radius = 15
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

    def set_radius(self, radius):
        self.radius = radius
        size = radius * 2
        center = self.rect.center
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 0), (radius, radius), radius)
        self.rect = self.image.get_rect(center=center)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
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


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        pygame.sprite.Sprite.__init__(self)
        self.powerup_type = powerup_type
        self.radius = 15
        size = self.radius * 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, powerup_colours[powerup_type], (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    window.blit(img, (x, y))


def apply_powerup(powerup_type):
    global active_powerup, powerup_timer, scroll_speed, base_scroll_speed
    active_powerup = powerup_type
    powerup_timer = pygame.time.get_ticks()
    if logged_player:
        database.save_achievement(logged_player[0], 9)
    if powerup_type == "slow_motion":
        base_scroll_speed = scroll_speed
        scroll_speed = max(2, scroll_speed // 2)
    elif powerup_type == "shrink_bird":
        Bird.set_radius(8)


def remove_powerup():
    global active_powerup, scroll_speed
    if active_powerup == "slow_motion":
        scroll_speed = base_scroll_speed
    elif active_powerup == "shrink_bird":
        Bird.set_radius(15)
    active_powerup = None


def draw_game_over_screen():
    window.fill((0, 0, 0))
    over_font = pygame.font.SysFont("Impact", 90)
    small_font = pygame.font.SysFont("Impact", 50)
    over_text = over_font.render("GAME OVER", True, white)
    score_text = small_font.render(f"Score: {score}", True, white)
    retry_button = pygame.Rect(width // 2 - 150, 420, 300, 60)
    menu_button = pygame.Rect(width // 2 - 150, 520, 300, 60)
    window.blit(over_text, (width // 2 - over_text.get_width() // 2, 200))
    window.blit(score_text, (width // 2 - score_text.get_width() // 2, 330))
    pygame.draw.rect(window, (0, 200, 0), retry_button, border_radius=10)
    pygame.draw.rect(window, (0, 200, 0), menu_button, border_radius=10)
    window.blit(small_font.render("Retry", True, white),
                (width // 2 - small_font.size("Retry")[0] // 2, 430))
    window.blit(small_font.render("Main Menu", True, white),
                (width // 2 - small_font.size("Main Menu")[0] // 2, 530))
    pygame.display.update()
    return retry_button, menu_button


def draw_pause_menu():
    overlay = pygame.Surface((400, 450))
    overlay.fill((240, 240, 240))
    overlay.set_alpha(230)
    overlay_rect = overlay.get_rect(center=(width // 2, height // 2))
    window.blit(overlay, overlay_rect)
    pause_font = pygame.font.SysFont("Impact", 50)
    button_font = pygame.font.SysFont("Impact", 40)
    small_font = pygame.font.SysFont("Impact", 30)
    black = (0, 0, 0)
    title = pause_font.render("Pause Menu", True, black)
    window.blit(title, (width // 2 - title.get_width() // 2, overlay_rect.y + 20))
    resume_button = pygame.Rect(width // 2 - 120, overlay_rect.y + 90, 240, 50)
    restart_button = pygame.Rect(width // 2 - 120, overlay_rect.y + 155, 240, 50)
    exit_button = pygame.Rect(width // 2 - 120, overlay_rect.y + 220, 240, 50)
    pygame.draw.rect(window, (0, 200, 0), resume_button, border_radius=8)
    pygame.draw.rect(window, (0, 200, 0), restart_button, border_radius=8)
    pygame.draw.rect(window, (200, 0, 0), exit_button, border_radius=8)
    window.blit(button_font.render("Resume", True, white),
                (width // 2 - button_font.size("Resume")[0] // 2, resume_button.y + 8))
    window.blit(button_font.render("Restart", True, white),
                (width // 2 - button_font.size("Restart")[0] // 2, restart_button.y + 8))
    window.blit(button_font.render("Exit", True, white),
                (width // 2 - button_font.size("Exit")[0] // 2, exit_button.y + 8))
    key_y = overlay_rect.y + 290
    window.blit(small_font.render("Power-Up Key:", True, black), (width // 2 - 120, key_y))
    powerup_display = [
        ("slow_motion", "Slow Motion"),
        ("invincibility", "Invincibility"),
        ("double_score", "Double Score"),
        ("shrink_bird", "Shrink Bird")
    ]
    for i, (ptype, pname) in enumerate(powerup_display):
        y = key_y + 35 + (i * 30)
        pygame.draw.circle(window, powerup_colours[ptype], (width // 2 - 100, y + 8), 10)
        window.blit(small_font.render(pname, True, black), (width // 2 - 80, y))
    pygame.display.update()
    return resume_button, restart_button, exit_button


def main_menu():
    menu_font = pygame.font.SysFont("Impact", 80)
    button_font = pygame.font.SysFont("Impact", 50)
    play_button = pygame.Rect(width // 2 - 150, 350, 300, 70)
    levels_button = pygame.Rect(width // 2 - 150, 450, 300, 70)
    leaderboard_button = pygame.Rect(width // 2 - 150, 550, 300, 70)
    achievements_button = pygame.Rect(width // 2 - 150, 650, 300, 70)

    while True:
        clock.tick(fps)
        window.fill((135, 206, 235))
        title = menu_font.render("MAIN MENU", True, white)
        window.blit(title, (width // 2 - title.get_width() // 2, 200))
        pygame.draw.rect(window, (0, 200, 0), play_button, border_radius=10)
        pygame.draw.rect(window, (0, 200, 0), levels_button, border_radius=10)
        pygame.draw.rect(window, (0, 200, 0), leaderboard_button, border_radius=10)
        pygame.draw.rect(window, (0, 200, 0), achievements_button, border_radius=10)
        window.blit(button_font.render("Play", True, white), (play_button.x + 90, play_button.y + 10))
        window.blit(button_font.render("Levels", True, white), (levels_button.x + 70, levels_button.y + 10))
        window.blit(button_font.render("Leaderboard", True, white), (leaderboard_button.x + 10, leaderboard_button.y + 10))
        window.blit(button_font.render("Achievements", True, white), (achievements_button.x + 10, achievements_button.y + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    main_game_loop()
                    return
                if levels_button.collidepoint(event.pos):
                    level_select()
                    return
                if leaderboard_button.collidepoint(event.pos):
                    leaderboard_screen()
                if achievements_button.collidepoint(event.pos):
                    achievements_screen()


def leaderboard_screen():
    menu_font = pygame.font.SysFont("Impact", 60)
    header_font = pygame.font.SysFont("Impact", 45)
    row_font = pygame.font.SysFont("Impact", 35)
    button_font = pygame.font.SysFont("Impact", 40)
    back_button = pygame.Rect(20, 20, 120, 50)
    endless_scores = database.get_leaderboard()

    while True:
        clock.tick(fps)
        window.fill((135, 206, 235))
        title = menu_font.render("LEADERBOARD", True, white)
        window.blit(title, (width // 2 - title.get_width() // 2, 30))
        pygame.draw.rect(window, (200, 0, 0), back_button, border_radius=8)
        window.blit(button_font.render("Back", True, white), (back_button.x + 10, back_button.y + 5))
        endless_header = header_font.render("Endless Mode", True, (255, 255, 100))
        window.blit(endless_header, (60, 110))
        if not endless_scores:
            window.blit(row_font.render("No scores yet!", True, white), (60, 160))
        else:
            for i, row in enumerate(endless_scores):
                username, row_score, time_survived, date = row
                line = row_font.render(f"{i+1}. {username}  {row_score} pipes  {date}", True, white)
                window.blit(line, (60, 160 + i * 50))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    main_menu()
                    return


def achievements_screen():
    menu_font = pygame.font.SysFont("Impact", 60)
    row_font = pygame.font.SysFont("Impact", 30)
    button_font = pygame.font.SysFont("Impact", 40)
    back_button = pygame.Rect(20, 20, 120, 50)

    achievements = database.get_player_achievements(logged_player[0]) if logged_player else []

    while True:
        clock.tick(fps)
        window.fill((135, 206, 235))
        title = menu_font.render("ACHIEVEMENTS", True, white)
        window.blit(title, (width // 2 - title.get_width() // 2, 30))
        pygame.draw.rect(window, (200, 0, 0), back_button, border_radius=8)
        window.blit(button_font.render("Back", True, white), (back_button.x + 10, back_button.y + 5))

        if not achievements:
            window.blit(row_font.render("No achievements unlocked yet!", True, white), (60, 160))
        else:
            for i, row in enumerate(achievements):
                ach_id, name, description, date = row
                pygame.draw.circle(window, (255, 215, 0), (60, 130 + i * 55), 12)
                window.blit(row_font.render(f"{name} - {description}", True, white), (85, 118 + i * 55))
                small = pygame.font.SysFont("Impact", 22)
                window.blit(small.render(f"Unlocked: {date}", True, (200, 255, 200)), (85, 143 + i * 55))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    main_menu()
                    return


def level_select():
    menu_font = pygame.font.SysFont("Impact", 70)
    button_font = pygame.font.SysFont("Impact", 50)
    back_button = pygame.Rect(20, 20, 120, 50)
    levels = [
        {"number": 1, "speed": 4, "gap": 150, "freq": 1500, "time": 30},
        {"number": 2, "speed": 6, "gap": 120, "freq": 1400, "time": 30},
        {"number": 3, "speed": 8, "gap": 110, "freq": 1300, "time": 30},
        {"number": 4, "speed": 10, "gap": 90, "freq": 1200, "time": 30},
        {"number": 5, "speed": 12, "gap": 80, "freq": 1100, "time": 30},
    ]
    level_buttons = []
    for i in range(5):
        btn = pygame.Rect(width // 2 - 150, 200 + i * 90, 300, 70)
        level_buttons.append(btn)

    while True:
        clock.tick(fps)
        window.fill((135, 206, 235))
        title = menu_font.render("SELECT LEVEL", True, white)
        window.blit(title, (width // 2 - title.get_width() // 2, 100))
        pygame.draw.rect(window, (200, 0, 0), back_button, border_radius=8)
        window.blit(button_font.render("Back", True, white), (back_button.x + 10, back_button.y + 5))
        for i, btn in enumerate(level_buttons):
            pygame.draw.rect(window, (0, 200, 0), btn, border_radius=10)
            window.blit(button_font.render(f"Level {i + 1}", True, white),
                        (width // 2 - button_font.size(f"Level {i + 1}")[0] // 2, btn.y + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    main_menu()
                    return
                for i, btn in enumerate(level_buttons):
                    if btn.collidepoint(event.pos):
                        level_game_loop(levels[i])
                        return


def level_game_loop(level):
    global flapping, over, pipe_pass, score, last_pipe, scroll_speed, pgap, pfreq
    global active_powerup, powerup_timer, Bird, death_count

    flapping = False
    over = False
    pipe_pass = False
    score = 0
    scroll_speed = level["speed"]
    pgap = level["gap"]
    pfreq = level["freq"]
    active_powerup = None

    time_limit = level["time"] * 1000
    start_ticks = pygame.time.get_ticks()
    last_pipe = pygame.time.get_ticks() - pfreq

    Bird.rect.center = (100, int(height / 2))
    Bird.vel = 0
    Bird.set_radius(15)
    pipe_group.empty()
    powerup_group.empty()

    paused = False
    resume_btn = restart_btn = exit_btn = None
    timer_font = pygame.font.SysFont("Impact", 50)

    run = True
    while run:
        clock.tick(fps)

        time_elapsed = pygame.time.get_ticks() - start_ticks
        time_remaining = max(0, (time_limit - time_elapsed) // 1000)

        if active_powerup and pygame.time.get_ticks() - powerup_timer >= POWERUP_DURATION:
            remove_powerup()

        if not paused:
            window.fill((135, 206, 235))

            player_group.update()
            pipe_group.update()
            powerup_group.update()

            pipe_group.draw(window)
            powerup_group.draw(window)
            player_group.draw(window)
            pygame.draw.rect(window, (34, 139, 34), (0, ground_y, 864, ground_height))

            draw_text(f"Level {level['number']}", timer_font, white, 20, 20)
            draw_text(f"Time: {time_remaining}s", timer_font, white, width - 220, 20)
            draw_text(str(score), font, white, int(width / 2), 20)

            if active_powerup:
                pu_font = pygame.font.SysFont("Impact", 35)
                time_left = (POWERUP_DURATION - (pygame.time.get_ticks() - powerup_timer)) // 1000
                draw_text(f"{powerup_names[active_powerup]}: {time_left}s", pu_font,
                          powerup_colours[active_powerup], 10, 80)

            if time_elapsed >= time_limit:
                if logged_player:
                    database.save_score(logged_player[0], level["number"], "level",
                                        time_survived=level["time"])
                level_complete(level)
                return

            # Score counting
            if len(pipe_group) > 0:
                if (player_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
                        and player_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right
                        and pipe_pass == False):
                    pipe_pass = True
                if pipe_pass == True:
                    if player_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                        score += 1
                        pipe_pass = False

            # Collision detection - skip if invincible
            if active_powerup != "invincibility":
                if pygame.sprite.groupcollide(player_group, pipe_group, False, False) or Bird.rect.top < 0:
                    over = True
                    run = False
                    # Death counter for "Persistent" achievement
                    global death_count
                    death_count += 1
                    if death_count >= 10 and logged_player:
                        database.save_achievement(logged_player[0], 7)

                if Bird.rect.bottom >= ground_y:
                    Bird.rect.bottom = ground_y
                    Bird.vel = 0
                    over = True
                    flapping = False
                    run = False
                    death_count += 1
                    if death_count >= 10 and logged_player:
                        database.save_achievement(logged_player[0], 7)

            # Power-up collision
            pu_hit = pygame.sprite.spritecollideany(Bird, powerup_group)
            if pu_hit:
                apply_powerup(pu_hit.powerup_type)
                pu_hit.kill()

            # Spawn pipes
            if not over and flapping:
                time_now = pygame.time.get_ticks()
                if time_now - last_pipe > pfreq:
                    pheight = random.randint(-100, 100)
                    b_pipe = Pipe(width, int(height / 2) + pheight, 1)
                    t_pipe = Pipe(width, int(height / 2) + pheight, -1)
                    pipe_group.add(b_pipe)
                    pipe_group.add(t_pipe)
                    last_pipe = time_now

                    if random.randint(1, 3) == 1 and not active_powerup:
                        pu_type = random.choice(powerup_types)
                        gap_centre = int(height / 2) + pheight
                        pu = PowerUp(width, gap_centre, pu_type)
                        powerup_group.add(pu)

            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if paused:
                    if resume_btn and resume_btn.collidepoint(event.pos):
                        paused = False
                    elif restart_btn and restart_btn.collidepoint(event.pos):
                        level_game_loop(level)
                        return
                    elif exit_btn and exit_btn.collidepoint(event.pos):
                        main_menu()
                        return
                elif not flapping and not over:
                    flapping = True

        if paused:
            resume_btn, restart_btn, exit_btn = draw_pause_menu()

    if logged_player:
        database.save_score(logged_player[0], level["number"], "level",
                            time_survived=time_remaining)

    while over:
        clock.tick(fps)
        retry_button, menu_button = draw_game_over_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    main_menu()
                    return
                if retry_button.collidepoint(event.pos):
                    level_game_loop(level)
                    return


def level_complete(level):
    window.fill((0, 0, 0))
    complete_font = pygame.font.SysFont("Impact", 80)
    small_font = pygame.font.SysFont("Impact", 50)
    complete_text = complete_font.render("LEVEL COMPLETE!", True, (0, 255, 0))
    level_text = small_font.render(f"Level {level['number']} Complete!", True, white)
    next_button = pygame.Rect(width // 2 - 150, 450, 300, 60)
    menu_button = pygame.Rect(width // 2 - 150, 540, 300, 60)
    window.blit(complete_text, (width // 2 - complete_text.get_width() // 2, 200))
    window.blit(level_text, (width // 2 - level_text.get_width() // 2, 330))
    pygame.draw.rect(window, (0, 200, 0), next_button, border_radius=10)
    pygame.draw.rect(window, (0, 200, 0), menu_button, border_radius=10)
    window.blit(small_font.render("Next Level", True, white),
                (width // 2 - small_font.size("Next Level")[0] // 2, 460))
    window.blit(small_font.render("Main Menu", True, white),
                (width // 2 - small_font.size("Main Menu")[0] // 2, 550))
    pygame.display.update()

    if logged_player:
        achievement_id = level["number"] + 1
        database.save_achievement(logged_player[0], achievement_id)

    levels = [
        {"number": 1, "speed": 4, "gap": 150, "freq": 1500, "time": 30},
        {"number": 2, "speed": 6, "gap": 120, "freq": 1400, "time": 30},
        {"number": 3, "speed": 8, "gap": 110, "freq": 1300, "time": 30},
        {"number": 4, "speed": 10, "gap": 90, "freq": 1200, "time": 30},
        {"number": 5, "speed": 12, "gap": 80, "freq": 1100, "time": 30},
    ]

    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.collidepoint(event.pos):
                    if level["number"] < 5:
                        level_game_loop(levels[level["number"]])
                        return
                    else:
                        main_menu()
                        return
                if menu_button.collidepoint(event.pos):
                    main_menu()
                    return


def main_game_loop():
    global flapping, over, pipe_pass, score, last_pipe, scroll_speed, pgap, pfreq
    global active_powerup, powerup_timer, Bird, base_scroll_speed, death_count

    flapping = False
    over = False
    pipe_pass = False
    score = 0
    scroll_speed = 4
    base_scroll_speed = 4
    pgap = 200
    pfreq = 1500
    active_powerup = None
    last_pipe = pygame.time.get_ticks() - pfreq

    Bird.rect.center = (100, int(height / 2))
    Bird.vel = 0
    Bird.set_radius(15)
    pipe_group.empty()
    powerup_group.empty()

    paused = False
    resume_btn = restart_btn = exit_btn = None

    run = True
    while run:
        clock.tick(fps)

        if active_powerup and pygame.time.get_ticks() - powerup_timer >= POWERUP_DURATION:
            remove_powerup()

        if not paused:
            window.fill((135, 206, 235))

            player_group.update()
            pipe_group.update()
            powerup_group.update()

            pipe_group.draw(window)
            powerup_group.draw(window)
            player_group.draw(window)
            pygame.draw.rect(window, (34, 139, 34), (0, ground_y, 864, ground_height))

            draw_text(str(score), font, white, int(width / 2), 20)
            if active_powerup:
                pu_font = pygame.font.SysFont("Impact", 35)
                time_left = (POWERUP_DURATION - (pygame.time.get_ticks() - powerup_timer)) // 1000
                draw_text(f"{powerup_names[active_powerup]}: {time_left}s", pu_font,
                          powerup_colours[active_powerup], 10, 10)

            # Collision detection - skip if invincible
            if active_powerup != "invincibility":
                if pygame.sprite.groupcollide(player_group, pipe_group, False, False) or Bird.rect.top < 0:
                    over = True
                    run = False
                    # Death counter for "Persistent" achievement
                    death_count += 1
                    if death_count >= 10 and logged_player:
                        database.save_achievement(logged_player[0], 7)

                if Bird.rect.bottom >= ground_y:
                    Bird.rect.bottom = ground_y
                    Bird.vel = 0
                    over = True
                    flapping = False
                    run = False
                    death_count += 1
                    if death_count >= 10 and logged_player:
                        database.save_achievement(logged_player[0], 7)

            # Power-up collision
            pu_hit = pygame.sprite.spritecollideany(Bird, powerup_group)
            if pu_hit:
                apply_powerup(pu_hit.powerup_type)
                pu_hit.kill()

            # Score counting
            if len(pipe_group) > 0:
                if (player_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
                        and player_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right
                        and pipe_pass == False):
                    pipe_pass = True
                if pipe_pass == True:
                    if player_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                        if active_powerup == "double_score":
                            score += 2
                        else:
                            score += 1
                        pipe_pass = False

                        if score % 5 == 0:
                            scroll_speed = min(scroll_speed + 0.5, 12)
                            base_scroll_speed = scroll_speed
                            pgap = max(pgap - 10, 100)
                            pfreq = max(pfreq - 50, 800)

            # Spawn pipes and powerups
            if not over and flapping:
                time_now = pygame.time.get_ticks()
                if time_now - last_pipe > pfreq:
                    pheight = random.randint(-100, 100)
                    b_pipe = Pipe(width, int(height / 2) + pheight, 1)
                    t_pipe = Pipe(width, int(height / 2) + pheight, -1)
                    pipe_group.add(b_pipe)
                    pipe_group.add(t_pipe)
                    last_pipe = time_now

                    if random.randint(1, 3) == 1 and not active_powerup:
                        pu_type = random.choice(powerup_types)
                        gap_centre = int(height / 2) + pheight
                        pu = PowerUp(width, gap_centre, pu_type)
                        powerup_group.add(pu)

            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if paused:
                    if resume_btn and resume_btn.collidepoint(event.pos):
                        paused = False
                    elif restart_btn and restart_btn.collidepoint(event.pos):
                        main_game_loop()
                        return
                    elif exit_btn and exit_btn.collidepoint(event.pos):
                        main_menu()
                        return
                elif not flapping and not over:
                    flapping = True

        if paused:
            resume_btn, restart_btn, exit_btn = draw_pause_menu()

    if logged_player:
        database.save_score(logged_player[0], None, "endless", score=score)
        if score >= 20:
            database.save_achievement(logged_player[0], 8)

    while over:
        clock.tick(fps)
        retry_button, menu_button = draw_game_over_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    main_menu()
                    return
                if retry_button.collidepoint(event.pos):
                    main_game_loop()
                    return


def start(player, login_window, login_clock):
    global logged_player, clock, window, font, player_group, Bird, pipe_group, last_pipe, powerup_group

    logged_player = player
    window = login_window
    clock = login_clock

    last_pipe = pygame.time.get_ticks() - pfreq
    pygame.display.set_caption("Flappy Bird")
    font = pygame.font.SysFont("Impact", 60)

    player_group = pygame.sprite.Group()
    Bird = Player(100, int(height / 2))
    player_group.add(Bird)
    pipe_group = pygame.sprite.Group()
    powerup_group = pygame.sprite.Group()

    if logged_player:
        database.save_achievement(logged_player[0], 1)

    main_menu()