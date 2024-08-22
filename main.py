import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
NEON_COLORS = [
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0),
    (0, 255, 0),
    (255, 69, 0),
]

PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 10
PADDLE_SPEED = 10
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
BALL_ACCELERATION = 1.02

BUFF_SIZE = 20
BUFF_DURATION = 10000

paddle1 = pygame.Rect(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - 40, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

score1 = 0
score2 = 0
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
ball_color = RED

buffs = []
buff_timer = 0
buffs_available = ['enlarge', 'shrink', 'faster', 'slower']
last_player = None
buff_messages = []
active_buffs = {1: None, 2: None}
buff_start_time = {1: None, 2: None}

clock = pygame.time.Clock()

burger_rect = pygame.Rect(WIDTH - 60, 20, 40, 40)

def draw_burger_icon():
    line_width = 5
    line_spacing = 10
    for i in range(3):
        pygame.draw.line(screen, WHITE, (burger_rect.left + 5, burger_rect.top + 10 + i * line_spacing),
                         (burger_rect.right - 5, burger_rect.top + 10 + i * line_spacing), line_width)

def reset_ball():
    global BALL_SPEED_X, BALL_SPEED_Y, ball_color
    ball.x = WIDTH // 2 - BALL_SIZE // 2
    ball.y = HEIGHT // 2 - BALL_SIZE // 2
    BALL_SPEED_X = random.choice([-5, 5])
    BALL_SPEED_Y = random.choice([-5, 5])
    ball_color = RED

def display_winner(winner):
    text = font.render(f"Winner: Player {winner}", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

def display_restart_quit_message():
    message = small_font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 + 50))

def spawn_buff():
    buff_type = random.choice(buffs_available)
    x = random.randint(BUFF_SIZE, WIDTH - BUFF_SIZE - BUFF_SIZE)
    y = random.randint(BUFF_SIZE, HEIGHT - BUFF_SIZE - BUFF_SIZE)
    color = random.choice(NEON_COLORS)
    return {'type': buff_type, 'rect': pygame.Rect(x, y, BUFF_SIZE, BUFF_SIZE), 'color': color, 'spawn_time': pygame.time.get_ticks()}

def apply_buff(player, buff):
    global PADDLE_WIDTH, PADDLE_HEIGHT
    if buff['type'] == 'enlarge':
        if player == 1:
            paddle1.height += 20
            return "Player 1: Paddle Enlarged"
        else:
            paddle2.height += 20
            return "Player 2: Paddle Enlarged"
    elif buff['type'] == 'shrink':
        if player == 1:
            paddle1.height = max(20, paddle1.height - 20)
            return "Player 1: Paddle Shrunk"
        else:
            paddle2.height = max(20, paddle2.height - 20)
            return "Player 2: Paddle Shrunk"
    elif buff['type'] == 'faster':
        active_buffs[player] = 'faster'
        return f"Player {player}: Paddle Faster"
    elif buff['type'] == 'slower':
        active_buffs[player] = 'slower'
        return f"Player {player}: Paddle Slower"

def display_buff_messages():
    y_offset = HEIGHT - 40
    for message, spawn_time in buff_messages:
        if pygame.time.get_ticks() - spawn_time < BUFF_DURATION:
            text = small_font.render(message, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset -= 30

def show_menu():
    screen.fill(BLACK)
    title = font.render("Paused", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    resume_message = small_font.render("Press ENTER to Resume", True, WHITE)
    screen.blit(resume_message, (WIDTH // 2 - resume_message.get_width() // 2, HEIGHT // 2))
    quit_message = small_font.render("Press Q to Quit", True, WHITE)
    screen.blit(quit_message, (WIDTH // 2 - quit_message.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    in_menu = True
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    in_menu = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    global score1, score2, BALL_SPEED_X, BALL_SPEED_Y, ball_color, buffs, last_player, buff_messages, active_buffs, buff_start_time

    buffs = [spawn_buff() for _ in range(3)]
    last_buff_time = pygame.time.get_ticks()
    buff_messages = []
    last_player = None
    active_buffs = {1: None, 2: None}
    buff_start_time = {1: None, 2: None}

    game_active = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if burger_rect.collidepoint(event.pos):
                    show_menu()

        keys = pygame.key.get_pressed()
        paddle1_speed = PADDLE_SPEED + 5 if active_buffs[1] == 'faster' else PADDLE_SPEED
        paddle2_speed = PADDLE_SPEED + 5 if active_buffs[2] == 'faster' else PADDLE_SPEED
        if active_buffs[1] == 'slower':
            paddle1_speed = max(5, paddle1_speed - 5)
        if active_buffs[2] == 'slower':
            paddle2_speed = max(5, paddle2_speed - 5)

        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= paddle1_speed
        if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
            paddle1.y += paddle1_speed
        if keys[pygame.K_UP] and paddle2.top > 0:
            paddle2.y -= paddle2_speed
        if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
            paddle2.y += paddle2_speed

        if game_active:
            ball.x += BALL_SPEED_X
            ball.y += BALL_SPEED_Y

            if ball.top <= 0 or ball.bottom >= HEIGHT:
                BALL_SPEED_Y = -BALL_SPEED_Y
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION

            if ball.left <= 0:
                score2 += 1
                last_player = 2
                if score2 >= 11:
                    game_active = False
                    display_winner(2)
                else:
                    reset_ball()
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION
                ball_color = GREEN

            if ball.right >= WIDTH:
                score1 += 1
                last_player = 1
                if score1 >= 11:
                    game_active = False
                    display_winner(1)
                else:
                    reset_ball()
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION
                ball_color = BLUE

            if ball.colliderect(paddle1) or ball.colliderect(paddle2):
                BALL_SPEED_X = -BALL_SPEED_X
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION

                if ball.colliderect(paddle1):
                    ball_color = BLUE
                    last_player = 1
                else:
                    ball_color = GREEN
                    last_player = 2

            current_time = pygame.time.get_ticks()
            if current_time - last_buff_time > 10000:
                last_buff_time = current_time
                buffs.append(spawn_buff())

            for buff in buffs[:]:
                if ball.colliderect(buff['rect']):
                    if last_player is not None:
                        message = apply_buff(last_player, buff)
                        buff_messages.append((message, pygame.time.get_ticks()))
                        buffs.remove(buff)
                        buff_start_time[last_player] = pygame.time.get_ticks()

            for player in [1, 2]:
                if buff_start_time[player] is not None:
                    if pygame.time.get_ticks() - buff_start_time[player] >= BUFF_DURATION:
                        if active_buffs[player] == 'enlarge' or active_buffs[player] == 'shrink':
                            if player == 1:
                                paddle1.height = 100
                            else:
                                paddle2.height = 100
                        active_buffs[player] = None
                        buff_start_time[player] = None

            screen.fill(BLACK)

            pygame.draw.rect(screen, BLUE, paddle1)
            pygame.draw.rect(screen, GREEN, paddle2)
            pygame.draw.ellipse(screen, ball_color, ball)

            for buff in buffs:
                pygame.draw.rect(screen, buff['color'], buff['rect'])

            score_text = font.render(f"{score1}  {score2}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

            display_buff_messages()

            draw_burger_icon()

            pygame.display.flip()

            clock.tick(60)
        else:
            screen.fill(BLACK)
            display_winner(1 if score1 >= 11 else 2)
            display_restart_quit_message()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        score1, score2 = 0, 0
                        reset_ball()
                        buffs = [spawn_buff() for _ in range(3)]
                        last_player = None
                        buff_messages = []
                        active_buffs = {1: None, 2: None}
                        buff_start_time = {1: None, 2: None}
                        game_active = True
                        break
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main()
