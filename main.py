import pygame
import sys
import random

# Initialize Pygame
pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)       # Color for Player 1
GREEN = (0, 255, 0)      # Color for Player 2
RED = (255, 0, 0)        # Color for Ball
NEON_COLORS = [
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (255, 69, 0),   # Orange-Red
]

# Paddle and ball properties
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 10
PADDLE_SPEED = 10
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
BALL_ACCELERATION = 1.02  # Reduced factor for ball speed increase

# Buffs/Debuffs properties
BUFF_SIZE = 20
BUFF_DURATION = 10000  # Duration of buffs/debuffs in milliseconds

# Create paddles and ball
paddle1 = pygame.Rect(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)  # Player 1 (left)
paddle2 = pygame.Rect(WIDTH - 40, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)  # Player 2 (right)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Score and ball color
score1 = 0
score2 = 0
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
ball_color = RED  # Initial ball color

# Buffs/Debuffs
buffs = []
buff_timer = 0
buffs_available = ['enlarge', 'shrink', 'faster', 'slower']
last_player = None  # Holds which player last touched the ball
buff_messages = []
active_buffs = {1: None, 2: None}  # Active buffs/debuffs for each player
buff_start_time = {1: None, 2: None}  # Track when each player's buff/debuff started

# Game loop
clock = pygame.time.Clock()

def reset_ball():
    global BALL_SPEED_X, BALL_SPEED_Y, ball_color
    ball.x = WIDTH // 2 - BALL_SIZE // 2
    ball.y = HEIGHT // 2 - BALL_SIZE // 2
    BALL_SPEED_X = random.choice([-5, 5])
    BALL_SPEED_Y = random.choice([-5, 5])
    ball_color = RED  # Reset ball color to Red

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
    global PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED
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
        PADDLE_SPEED += 5
        return "Player {}: Paddle Faster".format(player)
    elif buff['type'] == 'slower':
        PADDLE_SPEED = max(5, PADDLE_SPEED - 5)
        return "Player {}: Paddle Slower".format(player)

def display_buff_messages():
    y_offset = HEIGHT - 40
    for message, spawn_time in buff_messages:
        if pygame.time.get_ticks() - spawn_time < BUFF_DURATION:
            text = small_font.render(message, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset -= 30

def main():
    global score1, score2, BALL_SPEED_X, BALL_SPEED_Y, ball_color, buffs, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, last_player, buff_messages, active_buffs, buff_start_time

    # Start with buffs
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

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= PADDLE_SPEED
        if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
            paddle1.y += PADDLE_SPEED
        if keys[pygame.K_UP] and paddle2.top > 0:
            paddle2.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
            paddle2.y += PADDLE_SPEED

        if game_active:
            # Move the ball
            ball.x += BALL_SPEED_X
            ball.y += BALL_SPEED_Y

            # Ball collision with walls
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                BALL_SPEED_Y = -BALL_SPEED_Y
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION

            if ball.left <= 0:  # Player 2 scores a point
                score2 += 1
                last_player = 2
                if score2 >= 11:
                    game_active = False
                    display_winner(2)
                else:
                    reset_ball()
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION
                ball_color = GREEN  # Set ball color to Green

            if ball.right >= WIDTH:  # Player 1 scores a point
                score1 += 1
                last_player = 1
                if score1 >= 11:
                    game_active = False
                    display_winner(1)
                else:
                    reset_ball()
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION
                ball_color = BLUE  # Set ball color to Blue

            # Ball collision with paddles
            if ball.colliderect(paddle1) or ball.colliderect(paddle2):
                BALL_SPEED_X = -BALL_SPEED_X
                BALL_SPEED_X *= BALL_ACCELERATION
                BALL_SPEED_Y *= BALL_ACCELERATION

                # Change ball color based on which player hit it
                if ball.colliderect(paddle1):
                    ball_color = BLUE
                    last_player = 1
                else:
                    ball_color = GREEN
                    last_player = 2

            # Buffs/Debuffs appearance
            current_time = pygame.time.get_ticks()
            if current_time - last_buff_time > 10000:  # Buffs/Debuffs appear every 10 seconds
                last_buff_time = current_time
                buffs.append(spawn_buff())

            # Ball collision with buffs/debuffs
            for buff in buffs[:]:
                if ball.colliderect(buff['rect']):
                    # Determine message for buff/debuff
                    if last_player is not None:
                        message = apply_buff(last_player, buff)
                        buff_messages.append((message, pygame.time.get_ticks()))
                        buffs.remove(buff)
                        # Set the start time for the buff/debuff
                        buff_start_time[last_player] = pygame.time.get_ticks()

            # Check and remove expired buffs/debuffs
            for player in [1, 2]:
                if buff_start_time[player] is not None:
                    if pygame.time.get_ticks() - buff_start_time[player] >= BUFF_DURATION:
                        # Reset player effects
                        if active_buffs[player] == 'enlarge' or active_buffs[player] == 'shrink':
                            if player == 1:
                                paddle1.height = 100  # Reset height to default
                            else:
                                paddle2.height = 100  # Reset height to default
                        elif active_buffs[player] == 'faster' or active_buffs[player] == 'slower':
                            PADDLE_SPEED = 10  # Reset paddle speed to default
                        active_buffs[player] = None
                        buff_start_time[player] = None

            # Fill screen
            screen.fill(BLACK)

            # Draw paddles and ball
            pygame.draw.rect(screen, BLUE, paddle1)  # Player 1 in Blue
            pygame.draw.rect(screen, GREEN, paddle2)  # Player 2 in Green
            pygame.draw.ellipse(screen, ball_color, ball)  # Ball in the current color

            # Draw buffs/debuffs
            for buff in buffs:
                pygame.draw.rect(screen, buff['color'], buff['rect'])

            # Draw score
            score_text = font.render(f"{score1}  {score2}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

            # Draw buff/debuff messages
            display_buff_messages()

            # Update the screen
            pygame.display.flip()

            # Control the frame rate
            clock.tick(60)
        else:
            # Wait for user input to restart or quit the game
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
                        # Reset the game
                        score1, score2 = 0, 0
                        reset_ball()
                        buffs = [spawn_buff() for _ in range(3)]
                        PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
                        PADDLE_SPEED = 10
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
