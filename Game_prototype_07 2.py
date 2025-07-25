import pygame
import sys
from PIL import Image, ImageSequence
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Duo fight")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

def load_gif(filename, size=None):
    gif = Image.open(filename)
    frames = []
    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert('RGBA')
        if size:
            frame = frame.resize(size, Image.LANCZOS)
        pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
        frames.append(pygame_image)
    return frames

background_frames = load_gif("assets/background.gif", (WIDTH, HEIGHT))
background_index = 0
background_speed = 0.2

# เพิ่มเสียง
pygame.mixer.init()
ultimate_sound = pygame.mixer.Sound("assets/skill_sound.mp3")
skill_sound = pygame.mixer.Sound("assets/skill_sound.mp3")
ko_sound = pygame.mixer.Sound("assets/ko_sound.mp3")
gameover_sound = pygame.mixer.Sound("assets/game_over_sound.mp3")
dash_sound = pygame.mixer.Sound("assets/dash_sound.mp3")
attack_sound = pygame.mixer.Sound("assets/attack_sound.mp3")

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=10, character="ichigo"):
        super().__init__()
        self.frames = load_gif(f"assets/range_ichigo1_skill.gif", (50, 50))
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction
        self.speed = speed
        self.frame_index = 0
        self.animation_speed = 0.2

    def update(self):
        self.rect.x += self.speed * self.direction
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character, initial_direction):
        super().__init__()
        self.character = character
        self.load_images()
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 40
        self.speed = 5
        self.jump_power = -20
        self.gravity = 1.2
        self.vel_y = 0
        self.attacking = False
        self.attack_cooldown = 0
        self.frame_index = 0
        self.attack_frame_index = 0
        self.animation_speed = 0.2
        self.state = "idle"
        self.direction = initial_direction
        self.width = self.image.get_width()
        self.hp = 200
        self.combo_count = 0
        self.combo_timer = 0
        self.attack_animation_speed = [0.25, 0.3, 0.3]
        self.combo_cooldown = 80
        self.has_dealt_damage = False
        self.ultimate_cooldown = 0
        self.using_ultimate = False
        self.ultimate_frame_index = 0
        self.dashing = False
        self.dash_cooldown = 0
        self.dash_frame_index = 0
        self.dash_speed = 25
        self.dash_distance = 250
        self.using_skill = False
        self.skill_cooldown = 0
        self.skill_frame_index = 0
        self.stunned = False
        self.stun_timer = 0
        self.bleeding = False
        self.bleed_timer = 0
        self.bleed_frame_index = 0
        self.slashing = False
        self.slash_timer = 0
        self.slash_frame_index = 0
        self.slash_duration = 15
        self.taking_damage = False
        self.take_damage_timer = 0
        self.take_damage_frame_index = 0
        self.combo_effect = None
        self.combo_effect_timer = 0
        self.stamina = 0
        self.stamina_level = 0
        self.blocking = False
        self.skill_projectile = None
        self.block_frame_index = 0

    def load_images(self):
        if self.character == "ichigo":
            self.idle_frames = load_gif("assets/ichigo1_idle.gif", (100, 100))
            self.walk_frames = load_gif("assets/ichigo1_walk.gif", (100, 100))
            self.attack_frames = [
                load_gif("assets/ichigo1_attack_1.gif", (100, 100)),
                load_gif("assets/ichigo1_attack_2.gif", (140, 100)),
                load_gif("assets/ichigo1_attack_3.gif", (140, 100))
            ]
            self.ultimate_frames = load_gif("assets/ichigo_ultimate.gif", (WIDTH, HEIGHT))
            self.dash_frames = load_gif("assets/ichigo1_dash.gif", (100, 100))
            self.skill_frames = load_gif("assets/ichigo_skill.gif", (280, 150))
            self.take_damage_frames = load_gif("assets/ichigo1_take_damage.gif", (100, 100))
            self.block_frames = load_gif("assets/ichigo1_block.gif", (100, 100))
            self.combo_effect_frames = [
                load_gif("assets/combo_effect_1.gif", (150, 150)),
                load_gif("assets/combo_effect_2.gif", (200, 150)),
                load_gif("assets/combo_effect_3.gif", (150, 150))
            ]
        elif self.character == "naruto":
            self.idle_frames = load_gif("assets/naruto_idle.gif", (100, 100))
            self.walk_frames = load_gif("assets/naruto_walk.gif", (100, 100))
            self.attack_frames = [
                load_gif("assets/naruto_attack_1.gif", (100, 100)),
                load_gif("assets/naruto_attack_2.gif", (140, 100)),
                load_gif("assets/naruto_attack_3.gif", (140, 100))
            ]
            self.ultimate_frames = load_gif("assets/naruto_ultimate.gif", (WIDTH, HEIGHT))
            self.dash_frames = load_gif("assets/naruto_dash.gif", (100, 100))
            self.skill_frames = load_gif("assets/naruto_skill.gif", (280, 150))
            self.take_damage_frames = load_gif("assets/naruto_take_damage.gif", (100, 100))
            self.block_frames = load_gif("assets/naruto_block.gif", (100, 100))
            self.combo_effect_frames = None  # Naruto doesn't have combo effects

        self.bleed_frames = load_gif("assets/blood.gif", (150, 150))
        self.slash_frames = load_gif("assets/slash.gif", (200, 200))


    def move(self, direction):
        if not self.attacking and not self.dashing and not self.using_skill and not self.stunned and not self.taking_damage and not self.blocking:
            new_x = self.rect.x + direction * self.speed
            if 0 <= new_x <= WIDTH - self.width:
                self.rect.x = new_x
            self.direction = direction
            self.state = "walk"

    def stop_moving(self):
        if not self.attacking and not self.dashing and not self.using_skill and not self.stunned and not self.taking_damage and not self.blocking:
            self.state = "idle"

    def jump(self):
        if self.rect.bottom >= HEIGHT - 40 and not self.attacking and not self.stunned and not self.taking_damage and not self.blocking:
            self.vel_y = self.jump_power

    def attack(self):
        if not self.attacking and self.attack_cooldown == 0 and not self.using_skill and not self.stunned and not self.taking_damage and not self.blocking:
            self.attacking = True
            self.attack_cooldown = 30
            self.attack_frame_index = 0
            self.combo_count += 1
            if self.combo_count > 3:
                self.combo_count = 1
            self.combo_timer = self.combo_cooldown
            self.has_dealt_damage = False
            if self.character == "ichigo":
                self.combo_effect = self.combo_count - 1
                self.combo_effect_timer = 30
            attack_sound.play()

    def use_ultimate(self):
        if self.stamina >= 120 and self.ultimate_cooldown == 0 and not self.blocking:
            self.using_ultimate = True
            self.ultimate_frame_index = 0
            self.ultimate_cooldown = 600
            ultimate_sound.play()
            self.stamina = 0

    def dash(self, direction):
        if not self.dashing and self.dash_cooldown == 0 and not self.using_skill and not self.stunned and not self.taking_damage and not self.blocking:
            self.dashing = True
            self.dash_cooldown = 15
            self.dash_frame_index = 0
            self.direction = direction
            self.dash_distance_remaining = self.dash_distance
            dash_sound.play()

    def use_skill(self):
        if self.skill_cooldown == 0 and self.stamina >= 40 and not self.blocking:
            self.using_skill = True
            self.skill_frame_index = 0
            self.skill_cooldown = 300
            skill_sound.play()
            self.stamina -= 40
            self.skill_projectile = Projectile(self.rect.centerx, self.rect.centery, self.direction, character=self.character)

    def block(self):
        if not self.attacking and not self.dashing and not self.using_skill and not self.using_ultimate:
            self.blocking = True
            self.state = "block"
            self.block_frame_index = 0

    def stop_blocking(self):
        self.blocking = False
        if self.state == "block":
            self.state = "idle"

    def take_damage(self, damage):
        if not self.blocking:
            self.hp -= damage
            self.taking_damage = True
            self.take_damage_timer = 10
            self.take_damage_frame_index = 0
        else:
            self.hp -= damage // 2
            self.stamina = max(0, self.stamina - 8)
        if self.hp < 0:
            self.hp = 0
        self.stunned = True
        self.stun_timer = 12
        self.bleeding = True
        self.bleed_timer = 30
        self.bleed_frame_index = 0
        self.slashing = True
        self.slash_timer = self.slash_duration
        self.slash_frame_index = 0

    def increase_stamina(self, amount):
        self.stamina = min(120, self.stamina + amount)

    def update_stamina_level(self):
        self.stamina_level = self.stamina // 40

    def update(self):
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False

        if self.bleeding:
            self.bleed_timer -= 1
            if self.bleed_timer <= 0:
                self.bleeding = False

        if self.slashing:
            self.slash_timer -= 1
            if self.slash_timer <= 0:
                self.slashing = False

        if self.taking_damage:
            self.take_damage_timer -= 1
            if self.take_damage_timer <= 0:
                self.taking_damage = False

        if self.combo_effect is not None:
            self.combo_effect_timer -= 1
            if self.combo_effect_timer <= 0:
                self.combo_effect = None

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        if self.rect.bottom > HEIGHT - 40:
            self.rect.bottom = HEIGHT - 40
            self.vel_y = 0

        if self.dashing and not self.stunned and not self.taking_damage:
            dash_move = self.direction * self.dash_speed
            new_x = self.rect.x + dash_move
            if new_x < 0:
                new_x = 0
            elif new_x > WIDTH - self.width:
                new_x = WIDTH - self.width
            self.rect.x = new_x
            self.dash_distance_remaining -= abs(dash_move)
            if self.dash_distance_remaining <= 0:
                self.dashing = False

        if self.using_ultimate:
            self.ultimate_frame_index += 0.5
            if self.ultimate_frame_index >= len(self.ultimate_frames):
                self.using_ultimate = False
                self.ultimate_frame_index = 0
        elif self.attacking:
            current_attack_frames = self.attack_frames[self.combo_count - 1]
            self.image = current_attack_frames[int(self.attack_frame_index)]
            self.attack_frame_index += self.attack_animation_speed[self.combo_count - 1]
            if self.attack_frame_index >= len(current_attack_frames):
                self.attacking = False
                self.attack_frame_index = 0
                self.has_dealt_damage = False
        elif self.dashing:
            self.image = self.dash_frames[int(self.dash_frame_index)]
            self.dash_frame_index += 0.5
            if self.dash_frame_index >= len(self.dash_frames):
                self.dash_frame_index = 0
        elif self.using_skill:
            self.image = self.skill_frames[int(self.skill_frame_index)]
            self.skill_frame_index += 0.5
            if self.skill_frame_index >= len(self.skill_frames):
                self.using_skill = False
                self.skill_frame_index = 0
        elif self.taking_damage:
            self.image = self.take_damage_frames[int(self.take_damage_frame_index)]
            self.take_damage_frame_index += 0.2
            if self.take_damage_frame_index >= len(self.take_damage_frames):
                self.take_damage_frame_index = 0
        elif self.blocking:
            self.image = self.block_frames[int(self.block_frame_index)]
            if self.block_frame_index < len(self.block_frames) - 1:
                self.block_frame_index += 0.2
        else:
            if self.state == "idle":
                frames = self.idle_frames
            elif self.state == "walk":
                frames = self.walk_frames
            
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.image = frames[int(self.frame_index)]

        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= 1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0

        if self.skill_projectile:
            self.skill_projectile.update()
            if self.skill_projectile.rect.right < 0 or self.skill_projectile.rect.left > WIDTH:
                self.skill_projectile = None

    def get_attack_rect(self):
        if self.attacking:
            if self.direction == 1:
                attack_x = self.rect.right
                attack_width = 50
            else:
                attack_width = 50
                attack_x = self.rect.left - attack_width
            return pygame.Rect(attack_x, self.rect.y, attack_width, self.rect.height)
        return None

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        if self.bleeding:
            bleed_frame = self.bleed_frames[int(self.bleed_frame_index) % len(self.bleed_frames)]
            bleed_rect = bleed_frame.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(bleed_frame, bleed_rect)
            self.bleed_frame_index += 0.5
            if self.bleed_frame_index >= len(self.bleed_frames):
                self.bleed_frame_index = 0

        if self.slashing:
            slash_frame = self.slash_frames[int(self.slash_frame_index) % len(self.slash_frames)]
            slash_rect = slash_frame.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(slash_frame, slash_rect)
            self.slash_frame_index += 1
            if self.slash_frame_index >= len(self.slash_frames):
                self.slash_frame_index = 0

        if self.combo_effect is not None and self.character == "ichigo":
            combo_effect_frame = self.combo_effect_frames[self.combo_effect][int(self.combo_effect_timer / 5) % len(self.combo_effect_frames[self.combo_effect])]
            
            if self.direction == -1:
                combo_effect_frame = pygame.transform.flip(combo_effect_frame, True, False)
            
            combo_effect_rect = combo_effect_frame.get_rect()
            
            offset_x = 0
            offset_y = 10
            
            if self.direction == 1:
                combo_effect_rect.midleft = (self.rect.right - offset_x, self.rect.centery - offset_y)
            else:
                combo_effect_rect.midright = (self.rect.left + offset_x, self.rect.centery - offset_y)
            
            screen.blit(combo_effect_frame, combo_effect_rect)

        if self.skill_projectile:
            screen.blit(self.skill_projectile.image, self.skill_projectile.rect)

def draw_health_bars(screen, player1, player2):
    # HP bars
    pygame.draw.rect(screen, RED, (50, 50, 300, 20))
    pygame.draw.rect(screen, GREEN, (50, 50, player1.hp * 1.5, 20))
    pygame.draw.rect(screen, RED, (WIDTH - 350, 50, 300, 20))
    pygame.draw.rect(screen, GREEN, (WIDTH - 350 + (300 - player2.hp * 1.5), 50, player2.hp * 1.5, 20))

    # Stamina bars
    for i in range(3):
        pygame.draw.rect(screen, GRAY, (50 + i * 105, 80, 100, 15))
        pygame.draw.rect(screen, GRAY, (WIDTH - 350 + i * 105, 80, 100, 15))

    # Player 1 Stamina
    for i in range(3):
        if player1.stamina > i * 40:
            width = min(100, (player1.stamina - i * 40) * 100 / 40)
            color = YELLOW if player1.stamina < 120 else ORANGE if (pygame.time.get_ticks() // 200) % 2 == 0 else RED
            pygame.draw.rect(screen, color, (50 + i * 105, 80, width, 15))

    # Player 2 Stamina
    for i in range(3):
        if player2.stamina > i * 40:
            width = min(100, (player2.stamina - i * 40) * 100 / 40)
            color = YELLOW if player2.stamina < 120 else ORANGE if (pygame.time.get_ticks() // 200) % 2 == 0 else RED
            pygame.draw.rect(screen, color, (WIDTH - 350 + i * 105, 80, width, 15))

    # แสดงค่า HP เป็นตัวเลข
    font = pygame.font.Font(None, 36)
    hp_text1 = font.render(str(player1.hp), True, WHITE)
    hp_text2 = font.render(str(player2.hp), True, WHITE)
    screen.blit(hp_text1, (55, 50))
    screen.blit(hp_text2, (WIDTH - 345, 50))

def draw_timer(screen, time_left):
    font = pygame.font.Font(None, 36)
    timer_text = font.render(str(time_left), True, WHITE)
    timer_rect = timer_text.get_rect(center=(WIDTH // 2, 30))
    screen.blit(timer_text, timer_rect)

def draw_round_info(screen, current_round, player1_wins, player2_wins):
    font = pygame.font.Font(None, 36)
    round_text = font.render(f"Round {current_round}", True, WHITE)
    round_rect = round_text.get_rect(center=(WIDTH // 2, 60))
    screen.blit(round_text, round_rect)

    wins_text = font.render(f"P1: {player1_wins} - P2: {player2_wins}", True, WHITE)
    wins_rect = wins_text.get_rect(center=(WIDTH // 2, 90))
    screen.blit(wins_text, wins_rect)

def show_ko_screen(screen, winner):
    font = pygame.font.Font(None, 72)
    ko_text = font.render("KO!", True, RED)
    ko_rect = ko_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(ko_text, ko_rect)

    winner_text = font.render(f"{winner} wins!", True, WHITE)
    winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(winner_text, winner_rect)

    pygame.display.flip()
    ko_sound.play()
    pygame.time.wait(2000)

def show_draw_screen(screen):
    font = pygame.font.Font(None, 72)
    draw_text = font.render("DRAW!", True, WHITE)
    draw_rect = draw_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(draw_text, draw_rect)

    pygame.display.flip()
    pygame.time.wait(2000)

def show_game_over_screen(screen, winner):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(game_over_text, game_over_rect)

    winner_text = font.render(f"{winner} wins the match!", True, WHITE)
    winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(winner_text, winner_rect)

    instruction_font = pygame.font.Font(None, 36)
    instruction_text = instruction_font.render("Click anywhere to return to the main menu", True, WHITE)
    instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
    screen.blit(instruction_text, instruction_rect)

    pygame.display.flip()
    gameover_sound.play()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def show_home_screen(screen):
    background = pygame.image.load("assets/home_background.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))

    font = pygame.font.Font(None, 72)
    title_text = font.render("Duo fight", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(title_text, title_rect)

    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    pygame.draw.rect(screen, GREEN, start_button)
    button_font = pygame.font.Font(None, 36)
    button_text = button_font.render("Start Game", True, BLACK)
    button_text_rect = button_text.get_rect(center=start_button.center)
    screen.blit(button_text, button_text_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    waiting = False

def main():
    player1 = Player(100, HEIGHT - 90, "ichigo", 1)
    player2 = Player(WIDTH - 250, HEIGHT - 90, "naruto", -1)

    all_sprites = pygame.sprite.Group(player1, player2)

    clock = pygame.time.Clock()
    running = True

    current_round = 1
    player1_wins = 0
    player2_wins = 0

    background_index = 0
    background_speed = 0.2

    while running:
        show_home_screen(screen)

        round_start_time = pygame.time.get_ticks()
        round_duration = 120000  # 120 seconds in milliseconds
        while current_round <= 3 and (player1_wins < 2 and player2_wins < 2):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j:
                        player1.attack()
                    elif event.key == pygame.K_u:
                        player1.use_skill()
                    elif event.key == pygame.K_i:
                        player1.use_ultimate()
                    elif event.key == pygame.K_s:
                        player1.block()
                    elif event.key == pygame.K_RSHIFT:
                        player2.attack()
                    elif event.key == pygame.K_RCTRL:
                        player2.use_skill()
                    elif event.key == pygame.K_RETURN:
                        player2.use_ultimate()
                    elif event.key == pygame.K_DOWN:
                        player2.block()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_s:
                        player1.stop_blocking()
                    elif event.key == pygame.K_DOWN:
                        player2.stop_blocking()

            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_l]:
                if keys[pygame.K_a]:
                    player1.dash(-1)
                elif keys[pygame.K_d]:
                    player1.dash(1)
            else:
                if keys[pygame.K_a]:
                    player1.move(-1)
                elif keys[pygame.K_d]:
                    player1.move(1)
                else:
                    player1.stop_moving()
            if keys[pygame.K_w]:
                player1.jump()

            if keys[pygame.K_LEFT]:
                player2.move(-1)
            elif keys[pygame.K_RIGHT]:
                player2.move(1)
            else:
                player2.stop_moving()
            
            if keys[pygame.K_UP]:
                player2.jump()

            all_sprites.update()

            if player1.attacking and not player1.has_dealt_damage:
                attack_rect = player1.get_attack_rect()
                if attack_rect and attack_rect.colliderect(player2.rect):
                    print(f"Player 1 hit Player 2 with combo {player1.combo_count}!")
                    player2.take_damage(7)
                    player1.has_dealt_damage = True
                    player1.increase_stamina(8)

            if player2.attacking and not player2.has_dealt_damage:
                attack_rect = player2.get_attack_rect()
                if attack_rect and attack_rect.colliderect(player1.rect):
                    print(f"Player 2 hit Player 1 with combo {player2.combo_count}!")
                    player1.take_damage(7)
                    player2.has_dealt_damage = True
                    player2.increase_stamina(8)

            if player1.using_ultimate or player2.using_ultimate:
                if player1.using_ultimate:
                    player2.take_damage(4)
                if player2.using_ultimate:
                    player1.take_damage(4)

            if player1.skill_projectile:
                if player1.skill_projectile.rect.colliderect(player2.rect):
                    player2.take_damage(15)
                    player1.skill_projectile = None

            if player2.skill_projectile:
                if player2.skill_projectile.rect.colliderect(player1.rect):
                    player1.take_damage(15)
                    player2.skill_projectile = None

            background_index += background_speed
            if background_index >= len(background_frames):
                background_index = 0
            screen.blit(background_frames[int(background_index)], (0, 0))
            
            for sprite in all_sprites:
                sprite.draw(screen)
            
            draw_health_bars(screen, player1, player2)
            
            if player1.using_ultimate:
                ultimate_frame = player1.ultimate_frames[int(player1.ultimate_frame_index)]
                screen.blit(ultimate_frame, (0, 0))
            elif player2.using_ultimate:
                ultimate_frame = player2.ultimate_frames[int(player2.ultimate_frame_index)]
                screen.blit(ultimate_frame, (0, 0))

            time_left = max(0, (round_duration - (pygame.time.get_ticks() - round_start_time)) // 1000)
            draw_timer(screen, time_left)
            draw_round_info(screen, current_round, player1_wins, player2_wins)

            pygame.display.flip()

            clock.tick(60)

            if player1.hp <= 0 or player2.hp <= 0 or time_left == 0:
                if player1.hp > player2.hp:
                    winner = "Player 1"
                    player1_wins += 1
                elif player2.hp > player1.hp:
                    winner = "Player 2"
                    player2_wins += 1
                else:
                    winner = None

                if winner:
                    show_ko_screen(screen, winner)
                else:
                    show_draw_screen(screen)

                # Reset HP for the next round
                player1.hp = 200
                player2.hp = 200

                # Reset positions
                player1.rect.x = 100
                player1.rect.y = HEIGHT - 90
                player2.rect.x = WIDTH - 250
                player2.rect.y = HEIGHT - 90

                # Reset all temporary effects and animations
                player1.attacking = False
                player1.dashing = False
                player1.using_skill = False
                player1.using_ultimate = False
                player1.stunned = False
                player1.bleeding = False
                player1.slashing = False
                player1.taking_damage = False
                player1.blocking = False

                player2.attacking = False
                player2.dashing = False
                player2.using_skill = False
                player2.using_ultimate = False
                player2.stunned = False
                player2.bleeding = False
                player2.slashing = False
                player2.taking_damage = False
                player2.blocking = False

                current_round += 1
                if current_round <= 3 and (player1_wins < 2 and player2_wins < 2):
                    round_start_time = pygame.time.get_ticks()

        # Game over
        if player1_wins >= 2:
            final_winner = "Player 1"
        elif player2_wins >= 2:
            final_winner = "Player 2"
        else:
            if player1_wins > player2_wins:
                final_winner = "Player 1"
            elif player2_wins > player1_wins:
                final_winner = "Player 2"
            else:
                final_winner = "Draw"

        show_game_over_screen(screen, final_winner)

        # Reset game state for a new game
        current_round = 1
        player1_wins = 0
        player2_wins = 0
        player1.hp = 200
        player2.hp = 200
        player1.stamina = 0
        player2.stamina = 0
        player1.update_stamina_level()
        player2.update_stamina_level()
        player1.rect.x = 100
        player1.rect.y = HEIGHT - 90
        player2.rect.x = WIDTH - 250
        player2.rect.y = HEIGHT - 90

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

